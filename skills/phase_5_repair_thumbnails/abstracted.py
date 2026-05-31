"""
Gene Capsule: Thumbnail Repair for YouTube
Abstracted from Phase_5_REPAIR_THUMBNAILS.py
"""

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def repair_youtube_thumbnail(video_id, image_path, token_path='youtube_token.pickle'):
    """Set a custom thumbnail for a YouTube video.
    
    Args:
        video_id (str): YouTube video ID.
        image_path (str): Path to the thumbnail image file.
        token_path (str): Path to the OAuth token pickle file (default: youtube_token.pickle).
                          NOTE: This file must be trusted as it is loaded via pickle.
    """
    # Load credentials
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(image_path)
        ).execute()
        print(f"✅ Thumbnail set for video {video_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to set thumbnail for {video_id}: {e}")
        return False

if __name__ == "__main__":
    # Example usage (would be called via params in production)
    video_id = os.getenv('YT_VIDEO_ID')
    image_path = os.getenv('YT_THUMBNAIL_PATH')
    if not video_id or not image_path:
        print("❌ Please set YT_VIDEO_ID and YT_THUMBNAIL_PATH environment variables")
        exit(1)
    repair_youtube_thumbnail(video_id, image_path)
