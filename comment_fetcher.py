"""
Comment Fetcher Module
Handles fetching comments from various platforms using URLs
"""

import re
import requests
import json
import instaloader
from urllib.parse import urlparse
from youtube_comment_downloader import YoutubeCommentDownloader


def get_platform(url):
    """Identify platform from URL"""
    domain = urlparse(url).netloc.lower()
    if 'reddit.com' in domain:
        return 'reddit'
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'instagram.com' in domain:
        return 'instagram'
    return 'unknown'


def fetch_instagram_comments(url):
    """
    Fetch comments from Instagram post using Instaloader.
    Note: Instagram aggressively rate-limits anonymous access.
    """
    L = instaloader.Instaloader()
    
    # Try to extract shortcode
    shortcode = None
    match = re.search(r'instagram\.com/(?:p|reel)/([^/?#&]+)', url)
    if match:
        shortcode = match.group(1)
    
    if not shortcode:
        return None, "Could not identify Instagram post shortcode"

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        comments = []
        count = 0
        
        # Get caption first
        if post.caption:
            comments.append(post.caption)
            
        # Try to get comments
        # this often requires login, so we catch errors gracefully
        try:
            for comment in post.get_comments():
                comments.append(comment.text)
                count += 1
                if count >= 50:  # Limit to avoid bans
                    break
        except Exception as e:
            # If we encountered an error (like LoginRequired)
            if len(comments) <= 1:
                return None, "Instagram requires login to view these comments. Please Copy & Paste them manually into the box below."
            
        # If we successfully got comments, or partial comments
        if len(comments) <= 1:
             return None, "Instagram restricted comment access. Please Copy & Paste comments manually."

        return {
            'title': f"Instagram Post ({shortcode})",
            'comments': comments
        }, None

    except Exception as e:
        error_msg = str(e)
        if "login" in error_msg.lower() or "redirec" in error_msg.lower() or "401" in error_msg:
            return None, "Instagram restricted access. Please copy/paste comments manually."
        return None, f"Instagram Error: {error_msg}"


def fetch_reddit_comments(url):
    """
    Fetch comments from Reddit post using PRAW (Official API)
    """
    try:
        import praw
        reddit = praw.Reddit(
            client_id="9jVRT3NZnasn-5TY0fnSOA",
            client_secret="97K3G8C7C57LCEfNh5N-9IQ6HTZ_FQ",
            user_agent="sentiment_app_by_u/SeaMany4405",
            username="SeaMany4405",
            password="Bhushan@2025",
            requestor_kwargs={'timeout': 10}
        )
        submission = reddit.submission(url=url)
        submission.comments.replace_more(limit=0)
        comments = [comment.body for comment in submission.comments.list()[:100]]
        
        if comments:
            return {'title': submission.title, 'comments': comments}, None
    except Exception as praw_err:
        print(f"PRAW Error: {str(praw_err)}")

    # JSON Fallback
    try:
        clean_url = url.split('?')[0].rstrip('/') + '.json'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(clean_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            title = data[0]['data']['children'][0]['data']['title']
            comments = [c['data'].get('body') for c in data[1]['data']['children'] if c['kind'] == 't1']
            comments = [c for c in comments if c and c not in ['[deleted]', '[removed]']]
            if comments:
                return {'title': title, 'comments': comments}, None
        return None, f"Reddit blocked (403/429). (PRAW: {str(praw_err)})"
    except Exception as e:
        return None, f"Reddit JSON Error: {str(e)}"


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
    elif platform == 'instagram':
        return fetch_instagram_comments(url)
    else:
        return None, "Unsupported platform. Currently supporting Reddit, YouTube, and Instagram."
