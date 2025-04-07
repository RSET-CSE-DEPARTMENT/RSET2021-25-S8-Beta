# AIDCA (AI Data Conversational Assistant)

## Overview

AIDCA (AI Data Conversational Assistant) is a web-based application that allows users to interact with databases using natural language queries. By leveraging a transformer-based language model, AIDCA converts everyday English questions into executable SQL queries and presents the output in a user-friendly chat interface. It simplifies database access for non-technical users, helping them query and analyze data conversationally.

## Features

-   **Natural Language to SQL:** Converts human language queries into SQL using a fine-tuned T5-small model.
-   **Interactive Chat UI:** Dynamic chatbot interface for question input and result display.
-   **Database Selector:** Switch between multiple database schemas via a dropdown.
-   **Live SQL Results:** Executes SQL queries and returns real-time tabular data.
-   **Error Handling:** Graceful responses for invalid queries or processing issues.

## Tech Stack

-   **Frontend:** HTML, CSS, JavaScript
-   **Backend:** Flask (Python)
-   **Model:** T5-small (fine-tuned on WikiSQL)
-   **Database:** MySQL
-   **Libraries:** Transformers (HuggingFace), SQLAlchemy, Flask-CORS, pandas

## Getting Started

Refer to the individual README files for Backend and Frontend setup instructions. Here's a quick overview:

### Prerequisites

-   Python 3.8+
-   MySQL
-   Node.js (if you later switch to a frontend framework)

### Backend Setup

1.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the Flask server:**

    ```bash
    python app.py
    ```

### Frontend Setup

1.  Open `index.html` in a browser (or host via a simple Python server):

    ```bash
    python -m http.server
    ```

### Database Setup

1.  Place your `.db` files or connect to a MySQL instance.
2.  Ensure proper schema setup for SQL generation.

---

**Note:** For detailed instructions on setting up the backend and frontend components, please refer to the respective `README.md` files located in the `backend` and `frontend` directories.
