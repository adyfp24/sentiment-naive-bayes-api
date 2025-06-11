from flask import Flask, request, jsonify
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

app = Flask(__name__)

try:
    with open('sentiment_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('indonesian') + list(stopwords.words('english')))

def preprocess_text(text):
    """Clean and preprocess Indonesian text"""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s]|[\d_]', ' ', text)
    
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)

@app.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """Endpoint for sentiment analysis"""
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        if 'comment' not in data:
            return jsonify({"error": "Missing 'comment' field"}), 400
        
        comment = data['comment']
        processed_comment = preprocess_text(comment)
        
        prediction = model.predict([processed_comment])[0]
        
        sentiment_map = {
            -1: "negative",
            0: "neutral",
            1: "positive"
        }
        
        response = {
            "original_comment": comment,
            "processed_comment": processed_comment,
            "sentiment": sentiment_map.get(prediction, "unknown"),
            "prediction_score": int(prediction)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model_loaded": bool(model)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)