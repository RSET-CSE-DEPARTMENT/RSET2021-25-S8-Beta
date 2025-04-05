from lime.lime_text import LimeTextExplainer
import numpy as np
import tensorflow as tf
import pickle
import webbrowser
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load your model and tokenizer
model = tf.keras.models.load_model('textclassifiernew.h5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Define a function for LIME to interact with your model
class_names = ["Human", "AI"]

def predict_proba(texts):
    sequences = tokenizer.texts_to_sequences(texts)
    vocab_size = model.layers[0].input_dim  # Get vocabulary size from embedding layer
    # Clamp indices to be within the vocabulary range
    clamped_sequences = [[min(idx, vocab_size - 1) for idx in seq] for seq in sequences]
    max_sequence_length = model.input_shape[1]  # Get max sequence length from model
    padded_sequences = pad_sequences(clamped_sequences, maxlen=max_sequence_length, padding='post')
    predictions = model.predict(padded_sequences)
    return np.hstack((1 - predictions, predictions))  # For binary classification, LIME expects both class probabilities

# Initialize LIME
explainer = LimeTextExplainer(class_names=class_names)

# Input text to explain
input_text = "Air pollution is caused when pollutants like sulfur, carbon, nitrogen, particulates, ozone, acid, etc. are released into the atmosphere. The main cause of air pollutants is the combustion of fuels, which are mainly fossil fuel. Air pollutants are also caused due to the use of vehicles, factories, power plants, waste disposal, agriculture, industry, construction, mining, logging, fishing, forestry, sewage treatment, transportation and other activities. In addition, the emission of pollutants from the environment can be reduced by adopting renewable energies, promoting public transport, enforcing stricter regulations, reducing the amount of waste, improving the quality of the water, using less energy, recycling, minimizing the number of cars, building more green buildings, increasing the efficiency of energy use, decreasing the pollution of water and air, protecting the natural environment, preventing the spread of diseases, controlling the growth of pests, eliminating the effects of climate change, limiting the impact of pollution on the health of people, developing sustainable agriculture and forestry."
explanation = explainer.explain_instance(input_text, predict_proba, num_features=20)

explanation.save_to_file('lime_explanation.html')


# Visualize explanation
explanation.show_in_notebook(text=True)
webbrowser.open('lime_explanation.html')
