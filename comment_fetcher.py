"""
Comment Fetcher Module
Handles fetching comments from various platforms using URLs
"""

import re
import requests
import json
from urllib.parse import urlparse
from youtube_comment_downloader import YoutubeCommentDownloader


def get_platform(url):
    """Identify platform from URL"""
    domain = urlparse(url).netloc.lower()
    if 'reddit.com' in domain:
        return 'reddit'
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    return 'unknown'




def fetch_reddit_comments(url):
    """
    Fetch comments from Reddit post using PRAW (Official API)
    Tries multiple modes: Authenticated -> Read-Only -> JSON Fallback
    """
    credentials = {
        "client_id": "9jVRT3NZnasn-5TY0fnSOA",
        "client_secret": "97K3G8C7C57LCEfNh5N-9IQ6HTZ_FQ",
        "user_agent": "sentiment_app_by_u/SeaMany4405"
    }
    
    # 1. Try PRAW (Official API)
    import praw
    for mode in ['authenticated', 'read-only']:
        try:
            if mode == 'authenticated':
                reddit = praw.Reddit(
                    **credentials,
                    username="SeaMany4405",
                    password="Bhushan@2025",
                    requestor_kwargs={'timeout': 10}
                )
            else:
                # Read-Only doesn't require username/password and often bypasses login errors
                reddit = praw.Reddit(
                    **credentials,
                    requestor_kwargs={'timeout': 10}
                )

            submission = reddit.submission(url=url)
            submission.comments.replace_more(limit=0)
            comments = [comment.body for comment in submission.comments.list()[:100]]
            
            if comments:
                return {'title': submission.title, 'comments': comments}, None
        except Exception as e:
            print(f"Reddit PRAW {mode} failed: {str(e)}")
            continue

    # 2. JSON Fallback (Stealth Mode)
    try:
        clean_url = url.split('?')[0].rstrip('/') + '.json?limit=100'
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json',
            'Referer': 'https://www.google.com/'
        }
        res = requests.get(clean_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            title = data[0]['data']['children'][0]['data']['title']
            comments = [c['data'].get('body') for c in data[1]['data']['children'] if c['kind'] == 't1']
            comments = [c for c in comments if c and c not in ['[deleted]', '[removed]']]
            if comments:
                return {'title': title, 'comments': comments}, None
        
        return None, "Reddit is temporarily blocking our server. Please try again in 5 minutes or use a different URL."
    except Exception as e:
        return None, f"Final Reddit Access Error: {str(e)}"


def fetch_youtube_comments(url):
    """
    Fetch comments from YouTube video using youtube-comment-downloader
    """
    try:
        video_id = None
        if 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
        elif 'youtube.com/shorts' in url:
            video_id = url.split('shorts/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
            
        if not video_id:
            return None, "Could not identify YouTube video ID"

        # Use a session with a realistic user agent
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        })
        
        downloader = YoutubeCommentDownloader()
        comments = []
        count = 0
        
        # YoutubeCommentDownloader internally handles fetching
        generator = downloader.get_comments(video_id)
        
        for comment in generator:
            text = comment.get('text')
            if text:
                comments.append(text)
                count += 1
                if count >= 100: # Limit for speed
                    break
        
        if not comments:
             return None, "YouTube returned 0 comments. This might be a restriction or a private video."

        return {
            'title': f"YouTube Video ({video_id})",
            'comments': comments
        }, None

    except Exception as e:
        return None, f"YouTube Error: {str(e)}"


def fetch_comments(url):
    """
    Main entry point to fetch comments from URL
    """
    platform = get_platform(url)
    
    if platform == 'reddit':
        return fetch_reddit_comments(url)
    elif platform == 'youtube':
        return fetch_youtube_comments(url)
    else:
        return None, "Unsupported platform. Currently supporting Reddit and YouTube."
