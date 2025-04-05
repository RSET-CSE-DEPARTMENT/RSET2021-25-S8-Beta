from flask import Flask, render_template, request, jsonify, send_from_directory
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from lime.lime_text import LimeTextExplainer
import os
from werkzeug.utils import secure_filename
from gpt2 import humanize_text

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load the model and tokenizer
try:
    model = tf.keras.models.load_model('textclassifiernew.h5')
    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)
except Exception as e:
    print(f"Error loading model or tokenizer: {e}")
    model = None
    tokenizer = None

def predict_text(text):
    if model is None or tokenizer is None:
        raise Exception("Model or tokenizer not loaded properly")
        
    # Preprocess text
    texts = [text]
    new_sequences = tokenizer.texts_to_sequences(texts)
    
    # Handle out-of-vocabulary tokens and truncate indices
    vocab_size = model.layers[0].input_dim
    new_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in new_sequences]
    
    # Pad sequences
    max_sequence_length_train = model.input_shape[1]
    new_sequences = pad_sequences(new_sequences, maxlen=max_sequence_length_train, padding='post')
    
    # Make prediction
    prediction = model.predict(new_sequences)[0][0]
    
    # Generate LIME explanation
    class_names = ["Human", "AI"]
    explainer = LimeTextExplainer(class_names=class_names)
    explanation = explainer.explain_instance(text, predict_proba, num_features=20)
    
    # Save explanation to a temporary file
    explanation_path = os.path.join('static', 'lime_explanation.html')
    
    # Generate HTML with custom CSS
    exp_html = explanation.as_html()
    custom_css = """
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1A1A1A;
            padding: 20px;
        }
        .lime.top.labels {
            overflow: visible !important;
            max-height: none !important;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin: 15px 0;
        }
        .text-with-highlighted-words {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow: visible !important;
            max-height: none !important;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin: 15px 0;
            line-height: 1.6;
        }
        table.explanation {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .explanation td, .explanation th {
            padding: 8px 12px;
            border: 1px solid #e9ecef;
        }
        .explanation th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .explanation tr:nth-child(even) {
            background: #f8f9fa;
        }
    </style>
    """
    
    # Insert custom CSS into the HTML
    exp_html = exp_html.replace('</head>', f'{custom_css}</head>')
    
    # Save the modified HTML
    with open(explanation_path, 'w', encoding='utf-8') as f:
        f.write(exp_html)
    
    return prediction, explanation_path

def predict_proba(texts):
    if model is None or tokenizer is None:
        raise Exception("Model or tokenizer not loaded properly")
        
    sequences = tokenizer.texts_to_sequences(texts)
    vocab_size = model.layers[0].input_dim
    clamped_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in sequences]
    max_sequence_length_train = model.input_shape[1]
    padded_sequences = pad_sequences(clamped_sequences, maxlen=max_sequence_length_train, padding='post')
    predictions = model.predict(padded_sequences)
    return np.hstack((1 - predictions, predictions))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'text' not in request.form:
            return jsonify({'error': 'No text provided'}), 400
            
        text = request.form['text']
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
            
        prediction, explanation_path = predict_text(text)
        
        # Convert boolean to integer for JSON serialization
        is_ai = 1 if prediction > 0.51 else 0
        
        result = {
            'prediction': float(prediction),
            'is_ai': is_ai,
            'explanation_path': str(explanation_path)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    try:
        # Get parameters from URL
        text = request.args.get('text', '')
        is_ai = request.args.get('is_ai', '0')
        prediction = request.args.get('prediction', '0')
        explanation_path = request.args.get('explanation_path', '')
        
        # Validate parameters
        if not text or not is_ai or not prediction or not explanation_path:
            return render_template('index.html')
            
        return render_template('results.html')
    except Exception as e:
        return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/humanize_page')
def humanize_page():
    return render_template('humanize.html')

@app.route('/humanize', methods=['POST'])
def humanize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Use the humanize_text function from gpt2.py
        humanized_text = humanize_text(text)
        
        return jsonify({
            'humanized_text': humanized_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True) 