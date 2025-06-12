from pytube import YouTube
from youtube_comment_downloader import YoutubeCommentDownloader
import re

def get_youtube_comments(url, max_comments=100):
    """Scrape YouTube comments from a video URL"""
    try:
        # Extract video ID from URL
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id:
            return None
            
        video_id = video_id.group(1)
        
        # Get comments using youtube-comment-downloader
        downloader = YoutubeCommentDownloader()
        comments = []
        
        for comment in downloader.get_comments_from_url(url, sort_by=1):
            if comment['text']:
                comments.append(comment['text'])
            if len(comments) >= max_comments:
                break
                
        return comments
        
    except Exception as e:
        print(f"Error scraping comments: {e}")
        return None