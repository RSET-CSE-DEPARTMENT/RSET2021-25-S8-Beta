
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
file_path = r"D:\xampp\htdocs\doctor_prescription\Ocr_Chatbot\chatbot_model\medical_chatbot_dataset.csv"  
df = pd.read_csv(file_path)

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text

# Apply preprocessing
df['User Query'] = df['User Query'].apply(preprocess_text)

# Vectorization
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['User Query'])

def get_response(user_input, threshold=0.2):
    user_input = preprocess_text(user_input)
    user_tfidf = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_tfidf, tfidf_matrix)
    
    best_match_idx = np.argmax(similarities)
    best_score = similarities[0, best_match_idx]

    # Threshold check
    if best_score < threshold:
        return "I'm sorry, I didn't understand. Can you rephrase your question?"
    
    return df.iloc[best_match_idx]['Bot Response']

# Example Usage
user_query = "What are the symptoms of diabetes?"
response = get_response(user_query)
print(response)
