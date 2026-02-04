"""
Creator Analytics Module
Handles multi-source data aggregation and advanced business scoring logic.
"""

from sentiment_engine import SentimentAnalyzer
from comment_fetcher import fetch_comments
import uuid
from datetime import datetime

class CreatorAnalyzer:
    def __init__(self):
        self.analyzer = SentimentAnalyzer()

    def analyze_creator(self, name, urls, manual_data=None):
        """
        Analyze a creator based on multiple content sources (URLs AND Manual Text).
        Aggregates sentiment and calculates business metrics.
        
        manual_data: list of dicts {'platform': 'instagram', 'text': 'comments...', 'title': '...'}
        """
        if manual_data is None:
            manual_data = []

        aggregated_results = {
            'positive': [],
            'negative': [],
            'neutral': [],
            'total_count': 0,
            'platform_breakdown': {
                'youtube': {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0},
                'reddit': {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0},
                'other': {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
            },
            'sources': []
        }

        errors = []

        # 1. Process URLs
        for url in urls:
            if not url:
                continue

            # Fetch comments for this specific URL
            fetch_result, error = fetch_comments(url)
            
            if error:
                errors.append(f"Error fetching {url}: {error}")
                continue

            comments = fetch_result['comments']
            title = fetch_result['title']
            platform = self._identify_platform(url)

            # Analyze sentiment for this batch
            analysis = self.analyzer.analyze_comments(comments)

            # Aggregate Data
            aggregated_results['positive'].extend(analysis['positive'])
            aggregated_results['negative'].extend(analysis['negative'])
            aggregated_results['neutral'].extend(analysis['neutral'])
            
            # Update counts
            count_pos = len(analysis['positive'])
            count_neg = len(analysis['negative'])
            count_neu = len(analysis['neutral'])
            total = len(comments)
            
            aggregated_results['total_count'] += total
            
            # Update Platform Breakdown
            if platform in aggregated_results['platform_breakdown']:
                stats = aggregated_results['platform_breakdown'][platform]
                stats['positive'] += count_pos
                stats['negative'] += count_neg
                stats['neutral'] += count_neu
                stats['total'] += total

            aggregated_results['sources'].append({
                'url': url,
                'title': title,
                'platform': platform,
                'sentiment_summary': analysis['counts']
            })

        # 2. Process Manual Data
        for item in manual_data:
            text_block = item.get('text', '')
            platform = item.get('platform', 'other')
            title = item.get('title', 'Manual Entry')

            if not text_block:
                continue

            # Split text block into lines (comments)
            comments = [line.strip() for line in text_block.split('\n') if line.strip()]
            
            if not comments:
                continue

            # Analyze
            analysis = self.analyzer.analyze_comments(comments)

            # Aggregate
            aggregated_results['positive'].extend(analysis['positive'])
            aggregated_results['negative'].extend(analysis['negative'])
            aggregated_results['neutral'].extend(analysis['neutral'])
            
            # Update counts
            count_pos = len(analysis['positive'])
            count_neg = len(analysis['negative'])
            count_neu = len(analysis['neutral'])
            total = len(comments)
            
            aggregated_results['total_count'] += total
            
            # Update Platform Breakdown
            if platform in aggregated_results['platform_breakdown']:
                stats = aggregated_results['platform_breakdown'][platform]
            else:
                stats = aggregated_results['platform_breakdown']['other'] # fallback

            stats['positive'] += count_pos
            stats['negative'] += count_neg
            stats['neutral'] += count_neu
            stats['total'] += total
            
            aggregated_results['sources'].append({
                'url': 'manual',
                'title': f"{title} ({platform})",
                'platform': platform,
                'sentiment_summary': analysis['counts']
            })

        # Calculate Overall Scores & Recommendations
        business_metrics = self._calculate_business_metrics(aggregated_results)

        return {
            'creator_name': name,
            'timestamp': datetime.now().isoformat(),
            'stats': aggregated_results,
            'business_analysis': business_metrics,
            'errors': errors
        }

    def _identify_platform(self, url):
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'reddit.com' in url:
            return 'reddit'
        return 'other'

    def _calculate_business_metrics(self, data):
        """
        Calculate advanced business metrics based on user requirements.
        """
        total = data['total_count']
        if total == 0:
            return {
                'overall_score': 0,
                'recommendation_title': "Insufficient Data",
                'recommendation_detail': "Not enough comments to analyze.",
                'cult_following_score': 0
            }

        pos_count = len(data['positive'])
        neu_count = len(data['neutral'])
        neg_count = len(data['negative'])

        # Business Logic: Score is (Positive + Neutral) %
        # Why? Neutral usually means engagement without hate, which is safe for brands.
        # Strict logic: "Positive + Neutral" as the "Brand Safe" metric.
        
        brand_safe_count = pos_count + neu_count
        brand_safe_percentage = (brand_safe_count / total) * 100
        
        positive_percentage = (pos_count / total) * 100

        # Detailed Recommendation Logic
        title = ""
        detail = ""
        category = ""

        if brand_safe_percentage >= 80:
            category = "excellent"
            title = "🌟 Excellent Choice: Potential Cult Following"
            detail = (
                "This creator is HIGHLY RECOMMENDED. The audience is overwhelmingly positive or neutral, "
                "indicating a loyal 'cult-like' following. Great for brand safety."
            )
        elif 70 <= brand_safe_percentage < 80:
            category = "good"
            title = "✅ Good Choice: Moderate Engagement"
            detail = (
                "This creator has a decent reputation. The audience is generally positive, but there is some mixed feedback. "
                "Safe for most standard campaigns."
            )
        else:
            category = "danger"
            title = "⛔ Risky Choice: Significant Negative Sentiment"
            detail = (
                "Metric is below 70%. This indicates a polarizing or negative audience reaction. "
                "Review the negative comments carefully before proceeding."
            )

        return {
            'overall_score': round(brand_safe_percentage, 1),
            'positive_percentage': round(positive_percentage, 1),
            'recommendation_title': title,
            'recommendation_detail': detail,
            'category': category,
            'cult_following_indicator': "High" if brand_safe_percentage > 85 else "Medium" if brand_safe_percentage > 70 else "Low"
        }
