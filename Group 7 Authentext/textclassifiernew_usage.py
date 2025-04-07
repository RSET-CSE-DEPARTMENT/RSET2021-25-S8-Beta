import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# Load the saved model and Tokenizer instance
loaded_model = tf.keras.models.load_model('textclassifiernew.h5')
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
vocab_size = loaded_model.layers[0].input_dim  # Get vocabulary size from embedding layer
new_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in new_sequences]

# Pad sequences using the max sequence length from training
max_sequence_length_train = loaded_model.input_shape[1]  # Get original input length
new_sequences = pad_sequences(new_sequences, maxlen=max_sequence_length_train, padding='post')

# Make predictions
predictions = loaded_model.predict(new_sequences)
predictions_mean = predictions.mean()
print(full_text)
# Interpret predictions
print(predictions_mean)
#if predictions_mean > 0.90:
    #print(f'Text most likely written by AI. Probability of human authorship: {round(predictions_mean * 100, 2)}% (very low probability)')
#elif predictions_mean > 0.69:
    #print(f'Text most likely written by AI. Probability of human authorship: {round(predictions_mean * 100, 2)}% (low probability)')
if predictions_mean > 0.51:
    print(f'Text most likely written by AI or with the help of AI.')
#elif predictions_mean > 0.40:
    #print(f'Text most likely written by a human. Probability of human authorship: {round(predictions_mean * 100, 2)}% (high probability)')
else:
    print(f'Text most likely written by a human.')
