import argparse, requests, time, re

def _validate_instagram_id(id_string):
    """Validate that an Instagram ID is a positive integer"""
    return bool(re.match(r'^\d+$', str(id_string)))

def _validate_access_token(token):
    """Basic validation for access token format"""
    return bool(token and len(token) > 10)

def upload_via_cloudflare(access_token, instagram_account_id, tunnel_url, filename, caption):
    # Validate inputs
    if not _validate_access_token(access_token):
        return print("❌ Invalid access token format")
    if not _validate_instagram_id(instagram_account_id):
        return print("❌ Invalid Instagram Account ID format")
    
    public_url = f"{tunnel_url}/{filename}"
    print(f"\n🚀 Sending Cloudflare Tunnel URL to Meta: {public_url}")

    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 1. Create Container
    r = requests.post(f"https://graph.facebook.com/v22.0/{instagram_account_id}/media", data={
        'media_type': 'REELS', 'video_url': public_url, 'caption': caption
    }, headers=headers).json()

    c_id = r.get('id')
    if not c_id: 
        return print(f"❌ Error: {r}")

    print(f"⏳ Processing (Meta is pulling the video through Cloudflare)...")
    for i in range(20):
        status_resp = requests.get(f"https://graph.facebook.com/v22.0/{c_id}", params={'fields': 'status_code'}, headers=headers).json()
        status = status_resp.get('status_code')
        print(f"   [{i+1}] Status: {status}")
        
        if status == 'FINISHED': 
            break
        if status == 'ERROR': 
            return print(f"❌ Meta failed: {status_resp}")
        time.sleep(15)

    # 2. Publish
    print("🚀 Publishing now...")
    res = requests.post(f"https://graph.facebook.com/v22.0/{instagram_account_id}/media_publish", data={'creation_id': c_id}, headers=headers).json()

    if 'id' in res:
        print(f"🎉 SUCCESS! Reel is live: {res['id']}")
    else:
        print(f"❌ Publish Failed: {res}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Instagram Reel publishing via Cloudflare Tunnel")
    parser.add_argument("--access_token", required=True, help="Instagram Graph API access token")
    parser.add_argument("--instagram_account_id", required=True, help="Instagram Account ID")
    parser.add_argument("--tunnel_url", required=True, help="Base URL of the Cloudflare Tunnel")
    parser.add_argument("--filename", required=True, help="Name of the video file accessible via the tunnel")
    parser.add_argument("--caption", default="Built with TaoAI via Cloudflare Tunnel. #ai #automation #taoai", help="Caption for the Reel")
    args = parser.parse_args()
    upload_via_cloudflare(args.access_token, args.instagram_account_id, args.tunnel_url, args.filename, args.caption)