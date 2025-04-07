# Synapse Frontend

## Overview
This is the frontend of the Synapse project, built using **React.js**. It provides a user interface to interact with the OCR, chatbot, and other features of the platform.

### Prerequisites
- Node.js (v16+)
- npm or yarn

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/synapse.git
    cd synapse/frontend
    ```

2. Install dependencies:
    ```bash
    npm install  # or yarn install
    ```

### Running the Frontend
1. Start the development server:
    ```bash
    npm run dev  # or yarn dev
    ```

2. The frontend will be running at `http://localhost:3000`.

### Notes
- Ensure that the backend is running on `http://localhost:8000` (or update API URLs in the frontend accordingly).
- Configuration options like API keys and environment variables should be set in `.env`.

### Directory Structure
- **src/**: Contains all the React components and assets.
- **components/**: Individual UI components like `Features`, `Hero`, `OCRResult`, and `GeminiChat`.
- **assets/**: Images and other static assets.

