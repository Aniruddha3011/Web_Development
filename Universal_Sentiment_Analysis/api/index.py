from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Minimal App Initialization
app = Flask(__name__)
CORS(app)

# Global analyzer variable for lazy initialization (Cold-start safety)
_analyzer = None

def get_analyzer():
    """Lazily initialize the VADER analyzer to avoid heavy import logic on every cold start"""
    global _analyzer
    if _analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _analyzer = SentimentIntensityAnalyzer()
        except ImportError:
            # Fallback or error handled at request time
            return None
    return _analyzer

def safe_clean(text):
    """Minimal, safe text cleaning for serverless without heavy regex overhead"""
    if not text or not isinstance(text, str):
        return ""
    # Remove HTML and URLs simply
    import re
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'http\S+', '', text)
    return text.strip().lower()

@app.route('/', methods=['GET'])
def root():
    """Simple health check - Mandatory Requirement #8"""
    return "Universal Sentiment Analysis API: Status OK (Serverless Mode)"

@app.route('/predict', methods=['POST'])
def predict():
    """Robust prediction route - Mandatory Requirement #8"""
    try:
        # 1. Safe JSON extraction
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json(silent=True)
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing "text" field in JSON body'}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({'sentiment': 'Neutral', 'score': 0, 'note': 'Empty text'}), 200

        # 2. Get analyzer safely
        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({'error': 'Sentiment engine failed to initialize'}), 500

        # 3. Clean and Analyze
        cleaned = safe_clean(text)
        scores = analyzer.polarity_scores(cleaned)
        compound = scores.get('compound', 0)
        
        # 4. Determine Sentiment
        if compound >= 0.05:
            sentiment = 'Positive'
        elif compound <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
            
        return jsonify({
            'status': 'success',
            'sentiment': sentiment,
            'confidence': compound,
            'details': scores
        })

    except Exception as e:
        # Catch-all for runtime stability
        return jsonify({
            'status': 'error',
            'message': 'Internal processing error',
            'trace': str(e)
        }), 500

# STRICT: No app.run() here.
# STRICT: No scrapers, matplotlib, or nltk calls.
# STRICT: VADER is used directly via vaderSentiment library.
