from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import sys

# Add the current directory to path so relative imports work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from text_utils import clean_text

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')
CORS(app)

# Initialize VADER directly (No pickle, no downloads)
analyzer = SentimentIntensityAnalyzer()

@app.route('/')
def home():
    """Confirms the API is live - Requirement #7"""
    return "Universal Sentiment Analysis API is Live and Running on Vercel!"

@app.route('/predict', methods=['POST'])
def predict():
    """Single text prediction - Requirement #8"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        cleaned = clean_text(text)
        scores = analyzer.polarity_scores(cleaned)
        
        # Categorize
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'Positive'
        elif compound <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return jsonify({
            'text': text,
            'sentiment': sentiment,
            'scores': scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_list():
    """Legacy compatibility route for bulk analysis"""
    try:
        data = request.get_json()
        if not data or 'comments' not in data:
            return jsonify({'error': 'No comments provided'}), 400
        
        comments = data['comments']
        positive = []
        negative = []
        neutral = []
        
        for comment in comments:
            cleaned = clean_text(comment)
            score = analyzer.polarity_scores(cleaned)['compound']
            
            if score >= 0.05:
                positive.append(comment)
            elif score <= -0.05:
                negative.append(comment)
            else:
                neutral.append(comment)
        
        return jsonify({
            'results': {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'counts': {
                    'positive': len(positive),
                    'negative': len(negative),
                    'neutral': len(neutral),
                    'total': len(comments)
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Note: Scrapers (YouTube/Reddit/Instagram) removed per Requirement #3
# Note: app.run() removed per Requirement #2

# Expose app for Vercel
if __name__ == "__main__":
    # This is only for local testing, Vercel uses the 'app' variable directly
    pass
