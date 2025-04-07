# Synapse Backend

## Overview
This is the backend of the Synapse project, built using **FastAPI**. It handles OCR functionality, chatbot interactions, and various API endpoints to support the frontend.

### Prerequisites
- Python 3.8+
- Virtual environment (optional, but recommended)

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/synapse.git
    cd synapse/backend
    ```

2. Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Backend
1. Run the FastAPI app:
    ```bash
    uvicorn app.main:app --reload
    ```

2. The API will be running at `http://localhost:8000`. You can test it using tools like Postman or directly from the frontend.

### API Documentation
Once the backend is running, access the interactive API documentation at: `http://localhost:8000/docs`

This provides detailed information on available endpoints and their usage.

### Notes
- Ensure that any environment variables are properly configured in `.env`.
- The backend uses several services (OCR, chatbot) that may require API keys or additional configuration.


