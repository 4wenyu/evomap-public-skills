---
name: phase_5_instagram_cloudflare
description: Automated Instagram Reel publishing via Cloudflare Tunnel to avoid local file path issues.
version: 1.0.0
category: automation
---

# Phase 5 Instagram Cloudflare Skill

This skill automates publishing Instagram Reels by serving a video file through a Cloudflare Tunnel, then using the publicly accessible URL to create and publish a Reel via the Instagram Graph API.

## Overview

1. Construct a public URL using the Cloudflare Tunnel base URL and video filename
2. Use the public URL to create an Instagram media container (REELS type)
3. Poll the container until processing is finished
4. Publish the container to the Instagram feed

## Parameters

- `access_token`: Instagram Graph API access token (required)
- `instagram_account_id`: Instagram Account ID (required)
- `tunnel_url`: Base URL of the Cloudflare Tunnel (required)
- `filename`: Name of the video file accessible via the tunnel (required)
- `caption`: Caption for the Reel (optional, defaults to "Built with TaoAI via Cloudflare Tunnel. #ai #automation #taoai")

## Usage

This skill is designed to be run as a standalone script or imported as a module.

### As a Script

```bash
python Phase_5_instagram_CLOUDFLARE.py \
  --access_token "YOUR_ACCESS_TOKEN" \
  --instagram_account_id "YOUR_IG_ID" \
  --tunnel_url "https://xxxx.trycloudflare.com" \
  --filename "short_cn_025_FINAL.mp4" \
  --caption "Your custom caption"
```

### As a Module

```python
from Phase_5_instagram_CLOUDFLARE import upload_via_cloudflare

upload_via_cloudflare(
    access_token="YOUR_ACCESS_TOKEN",
    instagram_account_id="YOUR_IG_ID",
    tunnel_url="https://xxxx.trycloudflare.com",
    filename="short_cn_025_FINAL.mp4",
    caption="Your custom caption"
)
```

## Implementation Details

The skill performs the following steps:

1. **URL Construction**: Combines the tunnel URL and filename to create a publicly accessible video URL
2. **Container Creation**: Sends the public URL to Instagram Graph API to create a media container
3. **Status Polling**: Polls the container status every 15 seconds until it reaches `FINISHED` state (max 20 attempts)
4. **Publication**: Publishes the container using the `media_publish` endpoint

## Error Handling

- If container creation fails (no `id` in response), the skill exits with the error details
- If container processing fails (status becomes `ERROR`), the skill exits with the error response
- All errors are printed to stdout with descriptive messages

## Requirements

- Python 3.x
- `requests` library
- Active Cloudflare Tunnel serving the video file
- Internet access to graph.facebook.com

## Security Notes

- Never hardcode access tokens in the script
- Use environment variables or secure parameter passing in production
- The skill does not store or log sensitive parameters
- Ensure your Cloudflare Tunnel is properly secured if serving sensitive content

## Example

```bash
python Phase_5_instagram_CLOUDFLARE.py \
  --access_token "EAAAA..." \
  --instagram_account_id "17841400000000000" \
  --tunnel_url "https://boat-huge-enclosed-ryan.trycloudflare.com" \
  --filename "short_cn_025_FINAL.mp4" \
  --caption "Check out this automated Reel! #ai"
```