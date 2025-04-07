import os
import json
import google.generativeai as genai
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ==================== Load Trained Model ====================

# Path to the trained model
model_path = "C:/Users/gshan/OneDrive/Desktop/hugging/sql-training-1742097108/"  # Replace with your actual model path

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# ==================== Generate SQL Query from NLP ====================

def generate_sql_from_nlp(nl_query):
    """Generate SQL query using the fine-tuned T5 model."""
    inputs = tokenizer(nl_query, return_tensors="pt", truncation=True)
    output_tokens = model.generate(**inputs, max_length=256)
    sql_query = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    return sql_query

# ==================== Configure Gemini API ====================

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

genai.configure(api_key=GOOGLE_API_KEY)

# Database schema in JSON format
database_schema_json = {
    "tables": [
        {
            "name": "Students",
            "columns": [
                {"name": "StudentID", "type": "INT", "primaryKey": True},
                {"name": "Name", "type": "VARCHAR(100)"},
                {"name": "Age", "type": "INT"},
                {"name": "CoreSubject", "type": "VARCHAR(50)"}
            ]
        },
        {
            "name": "Medicines",
            "columns": [
                {"name": "MedicineID", "type": "INT", "primaryKey": True},
                {"name": "Name", "type": "VARCHAR(255)"},
                {"name": "Brand", "type": "VARCHAR(255)"},
                {"name": "Category", "type": "VARCHAR(100)"},
                {"name": "Price", "type": "DECIMAL(10,2)"},
                {"name": "StockQuantity", "type": "INT"},
                {"name": "ExpirationDate", "type": "DATE"}
            ]
        },
        {
            "name": "Suppliers",
            "columns": [
                {"name": "SupplierID", "type": "INT", "primaryKey": True},
                {"name": "SupplierName", "type": "VARCHAR(255)"},
                {"name": "ContactNumber", "type": "VARCHAR(20)"},
                {"name": "Email", "type": "VARCHAR(255)"},
                {"name": "Address", "type": "TEXT"}
            ]
        },
        {
            "name": "Orders",
            "columns": [
                {"name": "OrderID", "type": "INT", "primaryKey": True},
                {"name": "CustomerID", "type": "INT", "foreignKey": "Customers(CustomerID)"},
                {"name": "OrderDate", "type": "DATE"},
                {"name": "TotalAmount", "type": "DECIMAL(10,2)"}
            ]
        },
        {
            "name": "Customers",
            "columns": [
                {"name": "CustomerID", "type": "INT", "primaryKey": True},
                {"name": "FirstName", "type": "VARCHAR(255)"},
                {"name": "LastName", "type": "VARCHAR(255)"},
                {"name": "Phone", "type": "VARCHAR(20)"},
                {"name": "Email", "type": "VARCHAR(255)"},
                {"name": "Address", "type": "TEXT"}
            ]
        },
        {
            "name": "OrderDetails",
            "columns": [
                {"name": "OrderDetailID", "type": "INT", "primaryKey": True},
                {"name": "OrderID", "type": "INT", "foreignKey": "Orders(OrderID)"},
                {"name": "MedicineID", "type": "INT", "foreignKey": "Medicines(MedicineID)"},
                {"name": "Quantity", "type": "INT"},
                {"name": "PricePerUnit", "type": "DECIMAL(10,2)"}
            ]
        }

    ]
}

database_schema_string = json.dumps(database_schema_json, indent=4)

# ==================== Refine SQL with Gemini ====================

def refine_sql_with_gemini(t5_sql, database_schema_string, question):
    """Refine SQL query using Gemini AI."""
    model_gemini = genai.GenerativeModel('gemini-1.5-pro-latest')  # Ensure correct Gemini model

    prompt = f"""
    You are an expert SQL developer.
    User question: {question}
    Database Schema:
    {database_schema_string}

    Validate and correct the following SQL query against the provided schema. Optimize the query for performance. Return ONLY the corrected SQL.

    SQL:
    {t5_sql}
    """

    response = model_gemini.generate_content(prompt)
    return response.text.strip()

# ==================== Execute Pipeline ====================

if __name__ == "__main__":
    # Example Natural Language Input
    question = "name all orders placed on 02/03/2024"

    # Generate SQL using T5 Model
    initial_sql = generate_sql_from_nlp(question)
    print("Generated SQL Query (T5 Model):", initial_sql)

    # Refine SQL using Gemini API
    refined_sql = refine_sql_with_gemini(initial_sql, database_schema_string, question)
    print("Refined SQL Query :", refined_sql)
