import os
import pandas as pd
from googleapiclient.discovery import build
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API
API_KEY = os.getenv('API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Inisialisasi YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_video_comments(video_id, max_results=100):
    """
    Mengambil komentar dari video YouTube tertentu
    """
    comments = []
    next_page_token = None
    
    try:
        while True:
            # Request komentar dari API
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_results),
                pageToken=next_page_token,
                textFormat='plainText'
            ).execute()
            
            # Ekstrak komentar
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append([
                    comment['authorDisplayName'],
                    comment['publishedAt'],
                    comment['updatedAt'],
                    comment['likeCount'],
                    comment['textDisplay'],
                    video_id
                ])
            
            # Cek apakah sudah mencapai limit atau tidak ada halaman berikutnya
            if 'nextPageToken' in response:
                next_page_token = response['nextPageToken']
                max_results -= 100
                if max_results <= 0:
                    break
            else:
                break
                
    except Exception as e:
        print(f"Error saat mengambil komentar untuk video {video_id}: {str(e)}")
    
    return comments

def search_videos_by_keyword(keyword, max_results=10):
    """
    Mencari video YouTube berdasarkan keyword
    """
    search_response = youtube.search().list(
        q=keyword,
        part='id,snippet',
        maxResults=max_results,
        type='video',
        relevanceLanguage='id',  # Prioritaskan konten berbahasa Indonesia
        regionCode='ID'         # Prioritaskan konten dari Indonesia
    ).execute()
    
    video_ids = []
    video_details = []
    
    for item in search_response['items']:
        video_ids.append(item['id']['videoId'])
        video_details.append({
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'published_at': item['snippet']['publishedAt']
        })
    
    return video_ids, video_details

def main():
    # Keyword untuk kebijakan publik (sesuaikan dengan kebutuhan)
    keywords = [
        'kebijakan publik indonesia',
        'kinerja pemerintahan indonesia',
        'izin tambang raja ampat',
    ]
    
    all_comments = []
    all_video_details = []
    
    for keyword in keywords:
        print(f"\nMencari video dengan keyword: '{keyword}'")
        
        # Cari video berdasarkan keyword
        video_ids, video_details = search_videos_by_keyword(keyword, max_results=5)
        all_video_details.extend(video_details)
        
        # Ambil komentar dari setiap video
        for video_id in tqdm(video_ids, desc=f"Mengambil komentar untuk keyword '{keyword}'"):
            comments = get_video_comments(video_id, max_results=200)  # 200 komentar per video
            all_comments.extend(comments)
    
    # Simpan ke DataFrame
    comments_df = pd.DataFrame(all_comments, columns=[
        'author', 'published_at', 'updated_at', 'like_count', 'text', 'video_id'
    ])
    
    video_details_df = pd.DataFrame(all_video_details)
    
    # Simpan ke file CSV
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    comments_file = f'youtube_comments_{timestamp}.csv'
    videos_file = f'youtube_videos_{timestamp}.csv'
    
    comments_df.to_csv(comments_file, index=False, encoding='utf-8')
    video_details_df.to_csv(videos_file, index=False, encoding='utf-8')
    
    print(f"\nData berhasil disimpan:")
    print(f"- Komentar: {comments_file}")
    print(f"- Detail Video: {videos_file}")
    print(f"Total komentar yang berhasil dikumpulkan: {len(comments_df)}")

if __name__ == '__main__':
    main()