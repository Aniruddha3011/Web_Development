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
    Fetch comments from Reddit post using JSON endpoint (No API key needed)
    """
    # Ensure URL ends with .json
    clean_url = url.split('?')[0]
    if not clean_url.endswith('.json'):
        if clean_url.endswith('/'):
            json_url = clean_url + '.json'
        else:
            json_url = clean_url + '/.json'
    else:
        json_url = clean_url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(json_url, headers=headers)
        if response.status_code != 200:
            return None, f"Failed to fetch Reddit data: Status {response.status_code}"

        data = response.json()
        
        # Reddit JSON structure: [post_listing, comment_listing]
        post_data = data[0]['data']['children'][0]['data']
        title = post_data.get('title', 'Reddit Post')
        
        comments_data = data[1]['data']['children']
        comments = []
        
        for child in comments_data:
            if child['kind'] == 't1':  # t1 is comment
                body = child['data'].get('body')
                if body and body != '[deleted]' and body != '[removed]':
                    comments.append(body)
                    
        return {
            'title': title,
            'comments': comments
        }, None

    except Exception as e:
        return None, str(e)


def fetch_youtube_comments(url):
    """
    Fetch comments from YouTube video using youtube-comment-downloader
    """
    downloader = YoutubeCommentDownloader()
    comments = []
    
    try:
        # Extract video ID
        # Supports: youtube.com/watch?v=ID, youtu.be/ID, youtube.com/shorts/ID
        video_id = None
        if 'youtu.be' in url:
            video_id = url.split('/')[-1].split('?')[0]
        elif 'youtube.com/shorts' in url:
            video_id = url.split('shorts/')[-1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[-1].split('&')[0]
            
        if not video_id:
            return None, "Could not identify YouTube video ID"

        # Fetch comments (limit to recent 200 to be fast)
        count = 0
        generator = downloader.get_comments(video_id)
        
        for comment in generator:
            text = comment.get('text')
            if text:
                comments.append(text)
                count += 1
                if count >= 200:  # Limit for performance
                    break
        
        return {
            'title': f"YouTube Video ({video_id})",
            'comments': comments
        }, None

    except Exception as e:
        return None, str(e)


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
