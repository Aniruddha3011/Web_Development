"""
Universal Sentiment Analysis Platform - Flask Backend
Replaces Streamlit with Flask API
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import uuid
from datetime import datetime
from sentiment_engine import SentimentAnalyzer
from comment_fetcher import fetch_comments
from creator_analytics import CreatorAnalyzer

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize sentiment analyzer with existing model
analyzer = SentimentAnalyzer()
creator_analyzer = CreatorAnalyzer()

# Store analysis sessions in memory (can be replaced with database later)
sessions = {}


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze comments from any platform
    Expects JSON: {"comments": ["comment1", "comment2", ...], "title": "optional title"}
    """
    try:
        data = request.get_json()
        
        if not data or 'comments' not in data:
            return jsonify({'error': 'No comments provided'}), 400
        
        comments = data['comments']
        title = data.get('title', 'Untitled Analysis')
        
        if not comments or len(comments) == 0:
            return jsonify({'error': 'Comments list is empty'}), 400
        
        # Perform sentiment analysis
        results = analyzer.analyze_comments(comments)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        return jsonify({
            'session_id': session_id,
            'title': title,
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    """
    Fetch and analyze comments from a URL
    Expects JSON: {"url": "https://..."}
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        
        # Fetch comments
        fetch_result, error = fetch_comments(url)
        
        if error:
            return jsonify({'error': error}), 400
            
        comments = fetch_result['comments']
        title = fetch_result['title']
        
        if not comments or len(comments) == 0:
            return jsonify({'error': 'No comments found at this URL'}), 400
            
        # Perform sentiment analysis
        results = analyzer.analyze_comments(comments)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
        
        return jsonify({
            'session_id': session_id,
            'title': title,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Retrieve analysis results by session ID"""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(sessions[session_id])


@app.route('/api/demo', methods=['GET'])
def demo_data():
    """Provide demo data for testing"""
    demo_comments = [
        "This is amazing! I love it so much!",
        "Great work, keep it up!",
        "Absolutely fantastic content!",
        "This is terrible, I hate it.",
        "Worst thing I've ever seen.",
        "Not good at all, very disappointing.",
        "It's okay, nothing special.",
        "Meh, could be better.",
        "Average content.",
        "Incredible! Best video ever!",
        "So helpful, thank you!",
        "This changed my life!",
        "Boring and useless.",
        "Waste of time.",
        "Pretty good overall.",
        "Nice work!",
        "Awesome stuff!",
        "Terrible quality.",
        "Just okay.",
        "Excellent explanation!"
    ]
    
    results = analyzer.analyze_comments(demo_comments)
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'title': 'Demo Analysis',
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    return jsonify({
        'session_id': session_id,
        'title': 'Demo Analysis',
        'results': results
    })


@app.route('/api/creator/analyze', methods=['POST'])
def analyze_creator():
    """
    Analyze a creator profile provided multiple URLs
    Expects JSON: {"name": "Creator Name", "urls": ["url1", "url2", ...]}
    """
    try:
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({'error': 'No URLs provided'}), 400
            
        name = data.get('name', 'Unknown Creator')
        urls = data.get('urls', [])
        manual_data = data.get('manual_data', [])
        
        if len(urls) == 0 and len(manual_data) == 0:
             return jsonify({'error': 'Please provide at least one URL or Manual Text entry.'}), 400
            
        # Perform Creator Analysis
        analysis_result = creator_analyzer.analyze_creator(name, urls, manual_data)
        
        if analysis_result['stats']['total_count'] == 0:
             return jsonify({'error': 'Could not fetch any comments from the provided URLs. Check URLs and try again.'}), 400

        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'type': 'creator',
            'data': analysis_result
        }
        
        return jsonify({
            'session_id': session_id,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Universal Sentiment Analysis Platform")
    print("📊 Server running at http://localhost:5000")
    print("💡 Open your browser and navigate to the URL above")
    app.run(debug=True, port=5000)
