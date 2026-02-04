import re

def remove_emojis(text):
    """Remove emojis from text"""
    emoji_pattern = re.compile(
        pattern="["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r"", text)

def clean_text(text):
    """Standardized cleaning for Vercel Serverless"""
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    
    # Remove HTML tags (minimal approach to avoid BeautifulSoup dependency issues if it fails)
    text = re.sub(r"<.*?>", "", text)
    
    # Common contractions
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"don't", "do not", text)
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"it's", "it is", text)
    
    # Remove special chars but keep basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
    
    # Lowercase and strip
    text = text.lower().strip()
    
    # Emoji removal
    text = remove_emojis(text)
    
    return text
