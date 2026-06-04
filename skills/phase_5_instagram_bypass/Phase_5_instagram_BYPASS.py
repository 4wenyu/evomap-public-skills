import argparse, requests, time, re

def _validate_instagram_id(id_string):
    """Validate that an Instagram ID is a positive integer"""
    return bool(re.match(r'^\d+$', str(id_string)))

def _validate_access_token(token):
    """Basic validation for access token format"""
    return bool(token and len(token) > 10)

def bypass_upload(access_token, ig_id, video_path, caption):
    # Validate inputs
    if not _validate_access_token(access_token):
        return print("❌ Invalid access token format")
    if not _validate_instagram_id(ig_id):
        return print("❌ Invalid Instagram ID format")
    
    print("🚀 [1/4] Uploading to high-speed CDN (Catbox)...")
    try:
        with open(video_path, 'rb') as f:
            cdn_res = requests.post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': f})
        public_url = cdn_res.text
        if not public_url.startswith("http"):
            return print(f"❌ CDN Upload Failed: {public_url}")
        print(f"✅ CDN URL Secured: {public_url}")
    except Exception as e:
        return print(f"❌ File Error: {e}")

    headers = {'Authorization': f'Bearer {access_token}'}
    
    print("🚀 [2/4] Sending CDN URL to Meta...")
    res = requests.post(f"https://graph.facebook.com/v22.0/{ig_id}/media", data={
        'media_type': 'REELS', 'video_url': public_url, 'caption': caption
    }, headers=headers).json()

    c_id = res.get('id')
    if not c_id:
        return print(f"❌ Meta Container Error: {res}")

    print(f"⏳ [3/4] Meta is processing the video...")
    for i in range(25):
        status = requests.get(f"https://graph.facebook.com/v22.0/{c_id}", params={'fields': 'status_code'}, headers=headers).json().get('status_code')
        print(f"   Status: {status}")
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            return print(f"❌ Meta failed validation again. (Extremely rare from CDN)")
        time.sleep(10)

    print("🚀 [4/4] Publishing Reel to feed...")
    pub = requests.post(f"https://graph.facebook.com/v22.0/{ig_id}/media_publish", data={'creation_id': c_id}, headers=headers).json()

    if 'id' in pub:
        print(f"🎉 SUCCESS! Reel is officially LIVE. ID: {pub['id']}")
    else:
        print(f"❌ Final Publish Failed: {pub}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Instagram Reel publishing via CDN bypass (Catbox)")
    parser.add_argument("--access_token", required=True, help="Instagram Graph API access token")
    parser.add_argument("--ig_id", required=True, help="Instagram Account ID")
    parser.add_argument("--video_path", required=True, help="Absolute path to the video file to upload")
    parser.add_argument("--caption", default="Testing TaoAI automated pipeline via CDN Bypass! #ai #automation #taoai", help="Caption for the Reel")
    args = parser.parse_args()
    bypass_upload(args.access_token, args.ig_id, args.video_path, args.caption)