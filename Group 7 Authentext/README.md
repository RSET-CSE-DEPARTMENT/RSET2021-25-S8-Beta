<<<<<<< HEAD
# AI Text Classifier Web Application

This web application uses machine learning to analyze text and determine whether it was written by AI or a human. It provides explanations for its predictions using LIME (Local Interpretable Model-agnostic Explanations).

## Features

- Text input analysis
- Real-time character counter
- Confidence score visualization
- LIME explanation visualization
- Modern, responsive UI
- Error handling and user feedback

## Prerequisites

- Python 3.10 or later
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Make sure you have the following files in your project directory:
   - `textclassifiernew.h5` (your trained model)
   - `tokenizer.pickle` (your trained tokenizer)

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter or paste the text you want to analyze in the text area
2. Click the "Analyze Text" button
3. Wait for the analysis to complete
4. View the results, including:
   - Prediction (AI or Human)
   - Confidence score
   - LIME explanation visualization

## Project Structure

```
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files (CSS, JS, uploads)
├── templates/         # HTML templates
│   └── index.html     # Main page template
├── textclassifiernew.h5  # Trained model
└── tokenizer.pickle   # Trained tokenizer
```

## Error Handling

The application includes comprehensive error handling for:
- Empty text input
- File size limits
- Model loading issues
- Server errors

## Contributing

Feel free to submit issues and enhancement requests! 

