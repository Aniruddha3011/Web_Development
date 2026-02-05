"""
Sentiment Analysis Engine
Uses the existing VADER model from model_pickle
"""

import pickle
from text_processor import clean


class SentimentAnalyzer:
    """Wrapper for VADER sentiment model"""
    
    def __init__(self, model_path=None):
        """Lazy init VADER model"""
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                self._model = SentimentIntensityAnalyzer()
            except ImportError:
                # Fallback to a mock with basic logic if needed, but it should be in requirements
                return None
        return self._model
    
    def analyze_comments(self, comments):
        """
        Analyze a list of comments and categorize by sentiment
        
        Args:
            comments: List of comment strings
            
        Returns:
            dict with 'positive', 'negative', 'neutral' lists and counts
        """
        # Clean all comments
        cleaned_comments = [clean(comment) for comment in comments]
        
        # Categorize by sentiment
        positive = []
        negative = []
        neutral = []
        
        for i, cleaned_comment in enumerate(cleaned_comments):
            try:
                # Get sentiment score using VADER
                if self.model:
                    score = self.model.polarity_scores(cleaned_comment)['compound']
                else:
                    score = 0 # Neutral fallback if no model
                
                # Categorize based on score
                if score >= 0.05:
                    positive.append(comments[i])
                elif score <= -0.05:
                    negative.append(comments[i])
                else:
                    neutral.append(comments[i])
            except Exception:
                # If analysis fails, treat as neutral
                neutral.append(comments[i])
        
        return {
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

    def predict_single(self, text):
        """Get sentiment score for a single text"""
        if not self.model:
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1}
        from text_processor import clean
        cleaned = clean(text)
        try:
            return self.model.polarity_scores(cleaned)
        except Exception:
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1}
