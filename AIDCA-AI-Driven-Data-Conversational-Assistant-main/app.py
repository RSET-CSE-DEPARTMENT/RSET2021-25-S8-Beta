import os
import json
import logging
import re  # Added import for regex
import mysql.connector
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from NLP2SQLPY import generate_sql_from_nlp, refine_sql_with_gemini  # Import from NLP2SQLPY.py

# ==================== Flask App Initialization ====================
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Ensure session security

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

db_connection = None
db_connected = False

# ==================== Helper Functions ====================

def get_database_schema():
    """Fetch the database schema dynamically."""
    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        
        schema = {}
        for row in cursor.fetchall():
            table = row["TABLE_NAME"]
            column = row["COLUMN_NAME"]
            data_type = row["DATA_TYPE"]
            schema.setdefault(table, []).append({column: data_type})

        return schema
    except Exception as e:
        logging.error(f"Error fetching schema: {e}")
        return {}

def validate_db_connection():
    """Check if the database connection is active."""
    global db_connection, db_connected
    try:
        if db_connection is None or not db_connected:
            return False
        db_connection.ping(reconnect=True)  # Reconnect if disconnected
        return True
    except:
        db_connected = False
        return False

def clean_sql_output(sql_text):
    """Removes markdown-style code formatting from SQL output."""
    return re.sub(r"```sql|```", "", sql_text).strip()

# ==================== Flask Routes ====================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/check_connection", methods=["GET"])
def check_connection():
    return jsonify({"connected": db_connected})

@app.route("/dbconnect", methods=["GET", "POST"])
def dbconnect():
    """Connect to the MySQL database."""
    global db_connection, db_connected

    if request.method == "POST":
        try:
            host = request.form.get("host", "").strip()
            user = request.form.get("user", "").strip()
            password = request.form.get("password", "").strip()
            database = request.form.get("database", "").strip()

            if not host or not user or not database:
                return render_template("dbconnect.html", message="Host, user, and database are required.")

            db_connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            db_connected = True
            session["selected_database"] = database  # Store selected database

            return redirect(url_for("main"))
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return render_template("dbconnect.html", message=f"Error: {e}")

    return render_template("dbconnect.html")

@app.route("/main", methods=["GET", "POST"])
def main():
    """Main interface for selecting a database."""
    global db_connection, db_connected

    if not validate_db_connection():
        return redirect(url_for("dbconnect"))

    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SHOW DATABASES")
        databases = [db["Database"] for db in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching databases: {e}")
        return render_template("main.html", database=session.get("selected_database"), databases=[], message=f"Error: {e}")

    if request.method == "POST":
        new_database = request.form.get("database")
        try:
            cursor.execute(f"USE {new_database}")
            session["selected_database"] = new_database
            return render_template("main.html", database=new_database, databases=databases, message=f"Switched to database: {new_database}")
        except Exception as e:
            logging.error(f"Error changing database: {e}")
            return render_template("main.html", database=session.get("selected_database"), databases=databases, message=f"Error: {e}")

    return render_template("main.html", database=session.get("selected_database"), databases=databases)

@app.route("/execute_query", methods=["POST"])
def execute_query():
    """Executes a SQL query and returns results as a list of dictionaries."""
    global db_connection

    if not db_connected:
        return jsonify({"status": "error", "message": "Not connected to a database."})

    nl_query = request.json.get("query")
    if not nl_query:
        return jsonify({"status": "error", "message": "No query provided."})

    try:
        # NLP to SQL
        t5_sql = generate_sql_from_nlp(nl_query)
        logging.debug(f"T5 Generated SQL: {t5_sql}")

        # Fetch database schema dynamically
        database_schema_json = get_database_schema()  # Fetch actual schema

        # Refine SQL using Gemini
        refined_sql = refine_sql_with_gemini(t5_sql, json.dumps(database_schema_json, indent=4), nl_query)
        refined_sql = clean_sql_output(refined_sql)  # Clean SQL before execution
        logging.debug(f"Cleaned SQL: {refined_sql}")

        cursor = db_connection.cursor(dictionary=True)  # Enables fetching rows as dicts
        cursor.execute(refined_sql)

        if refined_sql.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return jsonify({"status": "success", "query": refined_sql, "columns": columns, "rows": result})

        db_connection.commit()
        return jsonify({"status": "success", "query": refined_sql, "message": "Query executed successfully."})

    except Exception as e:
        logging.error(f"Error in execute_query: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/disconnect", methods=["POST"])
def disconnect():
    """Disconnect from the database."""
    global db_connection, db_connected

    try:
        if db_connection:
            db_connection.close()
        db_connected = False
        session["selected_database"] = None
        return redirect(url_for("home"))
    except Exception as e:
        logging.error(f"Failed to disconnect: {e}")
        return jsonify({"status": "error", "message": f"Failed to disconnect: {e}"}), 500

# ==================== Run Flask App ====================
if __name__ == "__main__":
    app.run(debug=True, port=5001)
