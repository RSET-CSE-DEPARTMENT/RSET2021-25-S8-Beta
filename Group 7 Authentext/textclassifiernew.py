import pandas as pd
import tensorflow as tf
import logging
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, Callback
import pickle

# Setup logging
logging.basicConfig(filename="training_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

# Confirm GPU usage
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    logger.info(f"GPUs available: {[gpu.name for gpu in gpus]}")
else:
    logger.warning("No GPU detected, training will use CPU.")

# Custom callback for printing and logging
class TrainingLogger(Callback):
    def on_epoch_end(self, epoch, logs=None):
        log_message = f"Epoch {epoch + 1}: Loss = {logs['loss']:.4f}, Accuracy = {logs['accuracy']:.4f}, " \
                      f"Val Loss = {logs['val_loss']:.4f}, Val Accuracy = {logs['val_accuracy']:.4f}"
        print(log_message)
        logger.info(log_message)

# Reading data
df = pd.read_csv('AIHumannew.csv')

# Splitting the dataset by labels
df_human = df[df.iloc[:, 1] == 0]  # Label 0: Human
df_ai = df[df.iloc[:, 1] == 1]    # Label 1: AI

# Sampling 1000 entries each
df_human_sample = df_human.sample(n=20000, random_state=42)
df_ai_sample = df_ai.sample(n=20000, random_state=42)

# Combining the samples
df_sampled = pd.concat([df_human_sample, df_ai_sample]).sample(frac=1, random_state=42)  # Shuffle data

# Splitting text and labels
texts = df_sampled.iloc[:, 0].tolist()
labels = df_sampled.iloc[:, 1].tolist()

# Splitting into train and validation
texts_train, texts_val, labels_train, labels_val = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Tokenizing and padding
tokenizer_train = Tokenizer()
tokenizer_train.fit_on_texts(texts_train)
word_index_train = tokenizer_train.word_index
total_words_train = len(word_index_train) + 1

sequences_train = tokenizer_train.texts_to_sequences(texts_train)
sequences_val = tokenizer_train.texts_to_sequences(texts_val)

max_sequence_length_train = max([len(seq) for seq in sequences_train])
sequences_train = pad_sequences(sequences_train, maxlen=max_sequence_length_train, padding='post')
sequences_val = pad_sequences(sequences_val, maxlen=max_sequence_length_train, padding='post')

labels_train = tf.constant(labels_train)
labels_val = tf.constant(labels_val)

# Define the model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(total_words_train, 16, input_length=max_sequence_length_train),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(3, activation='relu'),  # Intermediate layer
    tf.keras.layers.Dense(1, activation='sigmoid')  # Output for binary classification
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00045),
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Define callbacks
es = EarlyStopping(monitor='val_loss', mode='min', patience=3, restore_best_weights=True)
training_logger = TrainingLogger()

# Train the model
history = model.fit(sequences_train, labels_train, epochs=30, batch_size=32, 
                    validation_data=(sequences_val, labels_val), callbacks=[es, training_logger])
model.save('textclassifiernew.h5')
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer_train, handle, protocol=pickle.HIGHEST_PROTOCOL)
