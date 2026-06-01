---
name: phase_5_instagram_bypass
description: Automated Instagram Reel publishing via CDN bypass (Catbox) to avoid Meta's direct file validation.
version: 1.0.0
category: automation
---

# Phase 5 Instagram Bypass Skill

This skill automates publishing Instagram Reels by first uploading the video to a public CDN (Catbox) to bypass Meta's direct file validation, then using the CDN URL to create and publish a Reel via the Instagram Graph API.

## Overview

1. Upload video to Catbox (https://catbox.moe) to get a public URL
2. Use the public URL to create an Instagram media container (REELS type)
3. Poll the container until processing is finished
4. Publish the container to the Instagram feed

## Parameters

- `access_token`: Instagram Graph API access token (required)
- `ig_id`: Instagram Account ID (required)
- `video_path`: Absolute path to the video file (required)
- `caption`: Caption for the Reel (optional, defaults to "Testing TaoAI automated pipeline via CDN Bypass! #ai #automation #taoai")

## Usage

This skill is designed to be run as a standalone script or imported as a module.

### As a Script

```bash
python Phase_5_instagram_BYPASS.py \
  --access_token "YOUR_ACCESS_TOKEN" \
  --ig_id "YOUR_IG_ID" \
  --video_path "/path/to/video.mp4" \
  --caption "Your custom caption"
```

### As a Module

```python
from Phase_5_instagram_BYPASS import bypass_upload

bypass_upload(
    access_token="YOUR_ACCESS_TOKEN",
    ig_id="YOUR_IG_ID",
    video_path="/path/to/video.mp4",
    caption="Your custom caption"
)
```

## Implementation Details

The skill performs the following steps:

1. **CDN Upload**: Uploads the video file to Catbox using a POST request to `https://catbox.moe/user/api.php`
2. **Container Creation**: Sends the CDN URL to Instagram Graph API to create a media container
3. **Status Polling**: Polls the container status every 10 seconds until it reaches `FINISHED` state (max 25 attempts)
4. **Publication**: Publishes the container using the `media_publish` endpoint

## Error Handling

- If CDN upload fails (non-HTTP response), the skill exits with an error message
- If container creation fails (no `id` in response), the skill exits with the error details
- If container processing fails (status becomes `ERROR`), the skill exits
- All errors are printed to stdout with descriptive messages

## Requirements

- Python 3.x
- `requests` library
- Internet access to Catbox.moe and graph.facebook.com

## Security Notes

- Never hardcode access tokens in the script
- Use environment variables or secure parameter passing in production
- The skill does not store or log sensitive parameters

## Example

```bash
python Phase_5_instagram_BYPASS.py \
  --access_token "EAAAA..." \
  --ig_id "17841400000000000" \
  --video_path "/home/user/videos/reel.mp4" \
  --caption "Check out this automated Reel! #ai"
```