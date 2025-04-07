import tensorflow as tf
import pickle
import numpy as np
import webbrowser
from tensorflow.keras.preprocessing.sequence import pad_sequences
from lime.lime_text import LimeTextExplainer

# Load the saved model and Tokenizer instance
model = tf.keras.models.load_model('textclassifiernew.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Load and preprocess text for prediction
full_text = open('text_to_predict.txt', encoding='iso-8859-1').read()
full_text = full_text.encode("latin-1").decode("utf-8")
split_text = full_text.split('\n')

# Filter and tokenize
texts = [line for line in split_text if len(line) > 20]  # Filter out short lines
new_sequences = tokenizer.texts_to_sequences(texts)

# Handle out-of-vocabulary tokens and truncate indices to match vocabulary size
vocab_size = model.layers[0].input_dim  # Get vocabulary size from embedding layer
new_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in new_sequences]

# Pad sequences using the max sequence length from training
max_sequence_length_train = model.input_shape[1]  # Get original input length
new_sequences = pad_sequences(new_sequences, maxlen=max_sequence_length_train, padding='post')

# Make predictions
predictions = model.predict(new_sequences)
predictions_mean = predictions.mean()
print(full_text)
print(f"Prediction Score: {predictions_mean:.4f}")

if predictions_mean > 0.51:
    print("Text most likely written by AI or with the help of AI.")
else:
    print("Text most likely written by a human.")

# Define function for LIME to interact with model
class_names = ["Human", "AI"]

def predict_proba(texts):
    sequences = tokenizer.texts_to_sequences(texts)
    clamped_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in sequences]
    padded_sequences = pad_sequences(clamped_sequences, maxlen=max_sequence_length_train, padding='post')
    predictions = model.predict(padded_sequences)
    return np.hstack((1 - predictions, predictions))  # LIME expects both class probabilities

# Initialize LIME and generate explanation
explainer = LimeTextExplainer(class_names=class_names)
explanation = explainer.explain_instance(full_text, predict_proba, num_features=20)
explanation.save_to_file('lime_explanation.html')

# Open explanation in a browser
webbrowser.open('lime_explanation.html')
