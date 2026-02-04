from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os
import re
import sys
import uuid
from datetime import datetime
from comment_fetcher import fetch_comments
from creator_analytics import CreatorAnalyzer

# --- Environment Setup ---
# BASE_DIR should point to the Universal_Sentiment_Analysis folder
# If running from api/index.py, it's one level up.
# If running from app.py, it's the current dir.
# We'll use a robust detection logic.
current_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(current_dir) == 'api':
    BASE_DIR = os.path.dirname(current_dir)
else:
    BASE_DIR = current_dir

# --- App Initialization ---
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
CORS(app)

# --- Lazy/Safe VADER Initialization ---
# We use a wrapper to handle any import-time or init-time issues
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            # We don't want to crash here, we'll return None and handle it in the route
            print(f"Analyzer Init Error: {str(e)}")
            return None
    return _analyzer

# --- Logic Layer ---
def clean_minimal(text):
    if not text or not isinstance(text, str):
        return ""
    # Remove HTML, URLs and non-ASCII for maximum stability
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip().lower()

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main frontend UI"""
    return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Renders the dashboard report UI"""
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handled prediction with robust JSON and logic checks"""
    try:
        if not request.is_json:
            return jsonify({'error': 'JSON required'}), 400
        
        data = request.get_json(silent=True)
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field'}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({'sentiment': 'Neutral', 'confidence': 0})

        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({'error': 'Sentiment engine error'}), 500

        cleaned = clean_minimal(text)
        scores = analyzer.polarity_scores(cleaned)
        compound = scores.get('compound', 0)
        
        sentiment = 'Neutral'
        if compound >= 0.05: sentiment = 'Positive'
        elif compound <= -0.05: sentiment = 'Negative'
            
        return jsonify({
            'status': 'success',
            'sentiment': sentiment,
            'confidence': compound,
            'details': scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy route for the frontend
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(silent=True)
        if not data or 'comments' not in data:
            return jsonify({'error': 'No comments'}), 400
        
        comments = data['comments']
        analyzer = get_analyzer()
        if not analyzer: return jsonify({'error': 'Engine error'}), 500

        results = {'positive': [], 'negative': [], 'neutral': []}
        for comment in comments:
            score = analyzer.polarity_scores(clean_minimal(comment))['compound']
            if score >= 0.05: results['positive'].append(comment)
            elif score <= -0.05: results['negative'].append(comment)
            else: results['neutral'].append(comment)
            
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        fetch_result, error = fetch_comments(url)
        if error:
            return jsonify({'error': error}), 400

        comments = fetch_result['comments']
        analyzer = get_analyzer()
        if not analyzer: return jsonify({'error': 'Engine error'}), 500

        results = {'positive': [], 'negative': [], 'neutral': []}
        for comment in comments:
            score = analyzer.polarity_scores(clean_minimal(comment))['compound']
            if score >= 0.05: results['positive'].append(comment)
            elif score <= -0.05: results['negative'].append(comment)
            else: results['neutral'].append(comment)
            
        return jsonify({
            'session_id': 'v-' + str(uuid.uuid4())[:8],
            'results': results,
            'title': fetch_result.get('title', 'Analysis Results')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/creator/analyze', methods=['POST'])
def analyze_creator():
    try:
        data = request.get_json(silent=True)
        if not data or 'name' not in data:
            return jsonify({'error': 'Missing name'}), 400
        
        ca = CreatorAnalyzer()
        results = ca.analyze_creator(
            name=data.get('name'), 
            urls=data.get('urls', []), 
            manual_data=data.get('manual_data', [])
        )
        
        return jsonify({
            'session_id': 'c-' + str(uuid.uuid4())[:8],
            'results': results['stats'], # Compatibility with dashboard
            'full_data': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo', methods=['GET'])
def demo():
    # Simple demo data
    results = {
        'positive': ['This is amazing!', 'Love the service.'],
        'negative': ['Could be better.', 'Too slow.'],
        'neutral': ['Its okay.', 'Standard.']
    }
    return jsonify({
        'session_id': 'demo-123',
        'results': results,
        'title': 'Demo Analysis'
    })

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    if isinstance(e, HTTPException):
        return jsonify(error=str(e.description)), e.code
    # Non-HTTP exceptions
    return jsonify(error="Internal Server Error: " + str(e)), 500

# Vercel entry point
if __name__ == "__main__":
    pass
