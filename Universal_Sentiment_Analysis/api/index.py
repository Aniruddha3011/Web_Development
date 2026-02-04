from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

# --- Minimal App Initialization ---
# Setting root_path ensures Flask finds 'templates' and 'static' in the project root
app = Flask(__name__, 
            root_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORS(app)

# --- Lazy Initialization for VADER ---
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            _analyzer = SentimentIntensityAnalyzer()
        except Exception:
            return None
    return _analyzer

# --- Self-Contained Cleaning Logic ---
def clean_text(text):
    if not text or not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove special emoji-like characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text.strip().lower()

# --- Routes ---

@app.route('/', methods=['GET'])
def health_check():
    """Confirms the API is alive and reachable"""
    return "Universal Sentiment Analysis API: Status 200 OK (Serverless Optimized)"

@app.route('/predict', methods=['POST'])
def predict():
    """Optimized prediction logic with robust error handling"""
    try:
        # Validate Request
        if not request.is_json:
            return jsonify({'error': 'Invalid request: Body must be JSON'}), 400
        
        data = request.get_json(silent=True)
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required "text" field'}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({'sentiment': 'Neutral', 'score': 0, 'status': 'empty_input'})

        # Get Analyzer
        analyzer = get_analyzer()
        if not analyzer:
            return jsonify({'error': 'Sentiment engine failed to initialize'}), 500

        # Analyze
        cleaned_input = clean_text(text)
        scores = analyzer.polarity_scores(cleaned_input)
        compound = scores.get('compound', 0)
        
        # Determine Sentiment
        if compound >= 0.05:
            sentiment = 'Positive'
        elif compound <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
            
        return jsonify({
            'status': 'success',
            'sentiment': sentiment,
            'score': compound,
            'details': scores
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_type': type(e).__name__,
            'message': str(e)
        }), 500

# Legacy compatibility route for bulk analyze (if frontend uses it)
@app.route('/api/analyze', methods=['POST'])
def analyze_bulk():
    try:
        data = request.get_json(silent=True)
        if not data or 'comments' not in data:
            return jsonify({'error': 'No comments found'}), 400
        
        comments = data['comments']
        analyzer = get_analyzer()
        if not analyzer: return jsonify({'error': 'Engine error'}), 500

        results = {'positive': [], 'negative': [], 'neutral': []}
        for comment in comments:
            score = analyzer.polarity_scores(clean_text(comment))['compound']
            if score >= 0.05: results['positive'].append(comment)
            elif score <= -0.05: results['negative'].append(comment)
            else: results['neutral'].append(comment)
            
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NO app.run() - Vercel handles invocation
