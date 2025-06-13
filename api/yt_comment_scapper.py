# from pytube import YouTube
# from youtube_comment_downloader import YoutubeCommentDownloader
# import re

# def get_youtube_comments(url, max_comments=100):
#     """Scrape YouTube comments from a video URL"""
#     try:
#         # Extract video ID from URL
#         video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
#         if not video_id:
#             return None
            
#         video_id = video_id.group(1)
        
#         # Get comments using youtube-comment-downloader
#         downloader = YoutubeCommentDownloader()
#         comments = []
        
#         for comment in downloader.get_comments_from_url(url, sort_by=1):
#             if comment['text']:
#                 comments.append(comment['text'])
#             if len(comments) >= max_comments:
#                 break
                
#         return comments
        
#     except Exception as e:
#         print(f"Error scraping comments: {e}")
#         return None


import csv
import re
from youtube_comment_downloader import YoutubeCommentDownloader

def get_youtube_comments(url, max_comments=4000, output_file="comments.csv"):
    """
    Scrape YouTube comments from a video URL and save to CSV.
    
    Args:
        url (str): YouTube video URL.
        max_comments (int): Maximum number of comments to scrape.
        output_file (str): Output CSV filename.
    """
    try:
        # Extract video ID from URL
        video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
        if not video_id:
            print("Invalid YouTube URL. Please check the URL format.")
            return None
            
        video_id = video_id.group(1)
        print(f"Scraping comments from video ID: {video_id}...")
        
        # Initialize comment downloader
        downloader = YoutubeCommentDownloader()
        
        # Open CSV file for writing
        with open(output_file, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Comment', 'Likes', 'Time', 'Author'])  # CSV header
            
            # Scrape comments
            count = 0
            for comment in downloader.get_comments_from_url(url, sort_by=1):  # sort_by=1 (Top Comments)
                if count >= max_comments:
                    break
                    
                # Write comment data to CSV
                writer.writerow([
                    comment['text'],
                    comment['votes'],
                    comment['time'],
                    comment['author']
                ])
                count += 1
                
                # Print progress every 100 comments
                if count % 100 == 0:
                    print(f"Scraped {count} comments...")
        
        print(f"Successfully saved {count} comments to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error scraping comments: {e}")
        return False


if __name__ == "__main__":
    # YouTube video URL (replace with your target)
    video_url = "https://www.youtube.com/watch?v=7CLZkPwhEG4"
    
    # Run scraper
    get_youtube_comments(video_url, max_comments=4000, output_file="comments.csv")