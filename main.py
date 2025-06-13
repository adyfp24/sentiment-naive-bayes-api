# import os
# import pandas as pd
# from googleapiclient.discovery import build
# from tqdm import tqdm
# from dotenv import load_dotenv

# load_dotenv()

# # Konfigurasi API
# API_KEY = os.getenv('API_KEY')
# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_VERSION = 'v3'

# # Inisialisasi YouTube API client
# youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

# def get_video_comments(video_id, max_results=100):
#     """
#     Mengambil komentar dari video YouTube tertentu
#     """
#     comments = []
#     next_page_token = None
    
#     try:
#         while True:
#             # Request komentar dari API
#             response = youtube.commentThreads().list(
#                 part='snippet',
#                 videoId=video_id,
#                 maxResults=min(100, max_results),
#                 pageToken=next_page_token,
#                 textFormat='plainText'
#             ).execute()
            
#             # Ekstrak komentar
#             for item in response['items']:
#                 comment = item['snippet']['topLevelComment']['snippet']
#                 comments.append([
#                     comment['authorDisplayName'],
#                     comment['publishedAt'],
#                     comment['updatedAt'],
#                     comment['likeCount'],
#                     comment['textDisplay'],
#                     video_id
#                 ])
            
#             # Cek apakah sudah mencapai limit atau tidak ada halaman berikutnya
#             if 'nextPageToken' in response:
#                 next_page_token = response['nextPageToken']
#                 max_results -= 100
#                 if max_results <= 0:
#                     break
#             else:
#                 break
                
#     except Exception as e:
#         print(f"Error saat mengambil komentar untuk video {video_id}: {str(e)}")
    
#     return comments

# def search_videos_by_keyword(keyword, max_results=10):
#     """
#     Mencari video YouTube berdasarkan keyword
#     """
#     search_response = youtube.search().list(
#         q=keyword,
#         part='id,snippet',
#         maxResults=max_results,
#         type='video',
#         relevanceLanguage='id',  # Prioritaskan konten berbahasa Indonesia
#         regionCode='ID'         # Prioritaskan konten dari Indonesia
#     ).execute()
    
#     video_ids = []
#     video_details = []
    
#     for item in search_response['items']:
#         video_ids.append(item['id']['videoId'])
#         video_details.append({
#             'video_id': item['id']['videoId'],
#             'title': item['snippet']['title'],
#             'channel': item['snippet']['channelTitle'],
#             'published_at': item['snippet']['publishedAt']
#         })
    
#     return video_ids, video_details

# def main():
#     # Keyword untuk kebijakan publik (sesuaikan dengan kebutuhan)
#     keywords = [
#         'kebijakan publik indonesia',
#         'kinerja pemerintahan indonesia',
#         'izin tambang raja ampat',
#     ]
    
#     all_comments = []
#     all_video_details = []
    
#     for keyword in keywords:
#         print(f"\nMencari video dengan keyword: '{keyword}'")
        
#         # Cari video berdasarkan keyword
#         video_ids, video_details = search_videos_by_keyword(keyword, max_results=5)
#         all_video_details.extend(video_details)
        
#         # Ambil komentar dari setiap video
#         for video_id in tqdm(video_ids, desc=f"Mengambil komentar untuk keyword '{keyword}'"):
#             comments = get_video_comments(video_id, max_results=200)  # 200 komentar per video
#             all_comments.extend(comments)
    
#     # Simpan ke DataFrame
#     comments_df = pd.DataFrame(all_comments, columns=[
#         'author', 'published_at', 'updated_at', 'like_count', 'text', 'video_id'
#     ])
    
#     video_details_df = pd.DataFrame(all_video_details)
    
#     # Simpan ke file CSV
#     timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
#     comments_file = f'youtube_comments_{timestamp}.csv'
#     videos_file = f'youtube_videos_{timestamp}.csv'
    
#     comments_df.to_csv(comments_file, index=False, encoding='utf-8')
#     video_details_df.to_csv(videos_file, index=False, encoding='utf-8')
    
#     print(f"\nData berhasil disimpan:")
#     print(f"- Komentar: {comments_file}")
#     print(f"- Detail Video: {videos_file}")
#     print(f"Total komentar yang berhasil dikumpulkan: {len(comments_df)}")

# if __name__ == '__main__':
#     main()

# import csv
# import re
# from youtube_comment_downloader import YoutubeCommentDownloader

# def get_youtube_comments(url, max_comments=4000, output_file="comments.csv"):
#     """
#     Scrape YouTube comments from a video URL and save to CSV.
    
#     Args:
#         url (str): YouTube video URL.
#         max_comments (int): Maximum number of comments to scrape.
#         output_file (str): Output CSV filename.
#     """
#     try:
#         # Extract video ID from URL
#         video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
#         if not video_id:
#             print("Invalid YouTube URL. Please check the URL format.")
#             return None
            
#         video_id = video_id.group(1)
#         print(f"Scraping comments from video ID: {video_id}...")
        
#         # Initialize comment downloader
#         downloader = YoutubeCommentDownloader()
        
#         # Open CSV file for writing
#         with open(output_file, mode='w', encoding='utf-8', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(['Comment', 'Likes', 'Time', 'Author'])  # CSV header
            
#             # Scrape comments
#             count = 0
#             for comment in downloader.get_comments_from_url(url, sort_by=1):  # sort_by=1 (Top Comments)
#                 if count >= max_comments:
#                     break
                    
#                 # Write comment data to CSV
#                 writer.writerow([
#                     comment['text'],
#                     comment['votes'],
#                     comment['time'],
#                     comment['author']
#                 ])
#                 count += 1
                
#                 # Print progress every 100 comments
#                 if count % 100 == 0:
#                     print(f"Scraped {count} comments...")
        
#         print(f"Successfully saved {count} comments to {output_file}")
#         return True
        
#     except Exception as e:
#         print(f"Error scraping comments: {e}")
#         return False


# if __name__ == "__main__":
#     # YouTube video URL (replace with your target)
#     video_url = "https://www.youtube.com/watch?v=7CLZkPwhEG4"
    
#     # Run scraper
#     get_youtube_comments(video_url, max_comments=4000, output_file="comments.csv")

import re
import pandas as pd
from youtube_comment_downloader import YoutubeCommentDownloader

def get_youtube_comments(url, max_comments=4000, output_file="comments.xlsx"):
    """
    Scrape YouTube comments from a video URL and save to Excel.
    
    Args:
        url (str): YouTube video URL.
        max_comments (int): Maximum number of comments to scrape.
        output_file (str): Output Excel filename (.xlsx).
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
        
        # Prepare data list
        comments_data = []
        
        # Scrape comments
        count = 0
        for comment in downloader.get_comments_from_url(url, sort_by=1):  # sort_by=1 (Top Comments)
            if count >= max_comments:
                break
                
            comments_data.append({
                'Comment': comment['text'],
                'Likes': comment['votes'],
                'Time': comment['time'],
                'Author': comment['author'],
                'Comment ID': comment['cid']  # Unique comment ID
            })
            count += 1
            
            # Print progress every 100 comments
            if count % 100 == 0:
                print(f"Scraped {count} comments...")
        
        # Convert to DataFrame
        df = pd.DataFrame(comments_data)
        
        # Save to Excel with auto-adjusted column widths
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Comments')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Comments']
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
        
        print(f"Successfully saved {count} comments to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error scraping comments: {e}")
        return False


if __name__ == "__main__":
    # YouTube video URL (replace with your target)
    video_url = "https://www.youtube.com/watch?v=7CLZkPwhEG4"
    
    # Run scraper
    get_youtube_comments(video_url, max_comments=4000, output_file="comments.xlsx")