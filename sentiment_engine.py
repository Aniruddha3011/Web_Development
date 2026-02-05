"""
Sentiment Analysis Engine
Uses the existing VADER model from model_pickle
"""

import pickle
from text_processor import clean


class SentimentAnalyzer:
    """Wrapper for VADER sentiment model"""
    
    def __init__(self, model_path='model_pickle'):
        """Load the pre-trained VADER model"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
    
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
                score = self.model.polarity_scores(cleaned_comment)['compound']
                
                # Categorize based on score
                if score > 0:
                    positive.append(comments[i])
                elif score < 0:
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

        # Calculate Brand Suitability Score
        # Formula: (Positive + Neutral) / Total * 100
        total_count = len(comments)
        if total_count > 0:
            positive_count = len(positive)
            neutral_count = len(neutral)
            brand_score = ((positive_count + neutral_count) / total_count) * 100
        else:
            brand_score = 0
            
        result['brand_score'] = round(brand_score, 1)
        result['brand_recommendation'] = "Excellent for Brand Collaboration! 🌟" if brand_score > 80 else "Needs Improvement for Promotions ⚠️"
        
        return result
        """Get sentiment score for a single text"""
        cleaned = clean(text)
        try:
            return self.model.polarity_scores(cleaned)
        except Exception:
            return {'compound': 0, 'pos': 0, 'neg': 0, 'neu': 1}
