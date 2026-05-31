---
name: phase_5_instagram_auto_gen
description: Instagram Reel auto-generator and uploader. Accepts access_token, ig_id, groq_key, and video path as arguments (no environment variables).
version: 1.0.0
category: automation
---
# Phase 5 Instagram Auto Gen

Instagram Reel auto-generator and uploader. Accepts access_token, ig_id, groq_key, and video path as arguments (no environment variables).

## Usage

See the abstracted implementation in `abstracted.py`.

## Abstracted Code

```python
"""
Gene Capsule: Instagram Reel Auto Generator
Abstracted from Phase_5_instagram_AUTO_GEN.py
"""

import sys
import json
import requests
import time
import os

def get_video_context(video_path):
    """Extract topic from accompanying JSON file or use default."""
    json_path = os.path.splitext(video_path)[0] + '.json'
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return data.get('topic', 'An amazing AI-generated video.')
    except FileNotFoundError:
        return "A high-tech cinematic overview created by the TaoAI Swarm."

def generate_ai_metadata(topic, groq_api_key):
    """Generate caption and comment using Groq API."""
    print(f"🧠 Generating dynamic caption via Groq for topic: '{topic}'...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}
    prompt = f"Write a punchy, engaging Instagram Reel caption (under 3 sentences) for a video about: {topic}. Include 3-5 relevant hashtags. Then, add the exact separator '|||', followed by a short, engaging first comment to boost algorithm engagement."
    
    try:
        r = requests.post(url, headers=headers, json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}).json()
        if 'choices' in r:
            result = r['choices'][0]['message']['content'].split('|||')
            return result[0].strip(), (result[1].strip() if len(result) > 1 else "What do you think? 👇")
        else:
            print(f"❌ Groq API Error: {r}")
            return "🔥 Automated AI Upload #ai", "Drop a comment!"
    except Exception as e:
        return "🔥 Automated AI Upload #ai", "Drop a comment!"

def upload_to_catbox(video_path):
    """Upload video to Catbox CDN and return public URL."""
    print("🚀 Uploading to high-speed CDN (Catbox)...")
    with open(video_path, 'rb') as f:
        public_url = requests.post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': f}).text
    if not public_url.startswith("http"):
        raise Exception(f"CDN Upload Failed: {public_url}")
    return public_url

def create_meta_container(ig_id, access_token, video_url, caption):
    """Create a Meta container for a Reel."""
    print("🚀 Creating Meta Container...")
    response = requests.post(
        f"https://graph.facebook.com/v22.0/{ig_id}/media",
        data={'media_type': 'REELS', 'video_url': video_url, 'caption': caption, 'comment_enabled': 'true', 'access_token': access_token}
    ).json()
    container_id = response.get('id')
    if not container_id:
        raise Exception(f"Meta Container Error: {response}")
    return container_id

def wait_for_transcoding(container_id, access_token, max_attempts=25, delay=10):
    """Wait for Meta to finish transcoding."""
    print("⏳ Waiting for Meta to finish transcoding...")
    for _ in range(max_attempts):
        status = requests.get(
            f"https://graph.facebook.com/v22.0/{container_id}",
            params={'fields': 'status_code', 'access_token': access_token}
        ).json().get('status_code')
        if status == 'FINISHED':
            print("✅ Transcoding finished.")
            return True
        time.sleep(delay)
    raise Exception("Transcoding timed out")

def publish_reel(ig_id, access_token, creation_id):
    """Publish the Reel from container."""
    print("🚀 Publishing Reel...")
    response = requests.post(
        f"https://graph.facebook.com/v22.0/{ig_id}/media_publish",
        data={'creation_id': creation_id, 'access_token': access_token}
    ).json()
    media_id = response.get('id')
    if not media_id:
        raise Exception(f"Final Publish Failed: {response}")
    print(f"🎉 SUCCESS! Reel LIVE. ID: {media_id}")
    return media_id

def post_comment(media_id, access_token, comment_text):
    """Post a comment on the published Reel."""
    print("💬 Posting AI-generated self-comment...")
    response = requests.post(
        f"https://graph.facebook.com/v22.0/{media_id}/comments",
        data={'message': comment_text, 'access_token': access_token}
    ).json()
    if 'id' in response:
        print(f"✅ Comment posted! ID: {response.get('id')}")
        return response.get('id')
    else:
        print(f"⚠️ Comment failed: {response}")
        return None

def auto_gen_upload(video_path, access_token, ig_id, groq_key):
    """Main workflow for automated Instagram Reel upload."""
    # Step 1: Get video context
    topic = get_video_context(video_path)
    
    # Step 2: Generate metadata
    caption, first_comment = generate_ai_metadata(topic, groq_key)
    print(f"\n📝 Caption: {caption}\n💬 Comment: {first_comment}\n")
    
    # Step 3: Upload to CDN
    public_url = upload_to_catbox(video_path)
    
    # Step 4: Create Meta container
    container_id = create_meta_container(ig_id, access_token, public_url, caption)
    
    # Step 5: Wait for transcoding
    wait_for_transcoding(container_id, access_token)
    
    # Step 6: Publish Reel
    media_id = publish_reel(ig_id, access_token, container_id)
    
    # Step 7: Post comment
    post_comment(media_id, access_token, first_comment)
    
    return media_id

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("❌ ERROR: You must provide access_token, ig_id, groq_key, and video file path.")
        print("Example: python3 abstracted.py <access_token> <ig_id> <groq_key> /path/to/video.mp4")
        sys.exit(1)
    access_token = sys.argv[1]
    ig_id = sys.argv[2]
    groq_key = sys.argv[3]
    video_path = sys.argv[4]
    auto_gen_upload(video_path, access_token, ig_id, groq_key)
```