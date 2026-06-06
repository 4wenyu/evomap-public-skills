import json
import os
import requests
from pathlib import Path

BASE_DIR = Path('/home/taoai/taoai-empire/taoai-empire')
SCRIPTS_DIR = BASE_DIR / "EXPORTS/scripts"
MASTER_JSON = BASE_DIR / "EXPORTS/video_data.json"

ENDPOINTS = [
    "http://localhost:8080/v1/chat/completions",
    "http://localhost:8080/chat/completions"
]

def get_local_response(prompt):
    payload = {
        # THE FIX: Tell the server exactly which model is loaded in memory!
        "model": "mlx-community/Qwen2.5-14B-Instruct-4bit",
        "messages": [
            {"role": "system", "content": "You are a Video Director. Output ONLY raw JSON. No markdown blocks. Return only a valid JSON object."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "stream": False
    }
    
    for url in ENDPOINTS:
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'], url
        except Exception:
            continue
            
    return None, None

def process_rescue():
    with open(MASTER_JSON, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    print("🏰 LOCAL EMPIRE RESCUE: Powering up Qwen 2.5 14B...")

    for video in master_data:
        vid_id = video['video_id']
        out_path = SCRIPTS_DIR / f"{vid_id}.json"
        
        if len(video.get("scenes", [])) < 3:
            print(f"🎬 Local Gen: {vid_id}...", end=" ", flush=True)
            
            prompt = f"""Generate a 5-scene JSON script for {vid_id}. 
            RULES:
            - Scene 1: type 'HOOK_LTX', visual_asset 'PENDING_LTX_GENERATION'.
            - Scenes 2-5: type 'B_ROLL'.
            - Output format: {{"scenes": [{{ "scene_number": 1, "scene_type": "HOOK_LTX", "spoken_text": "...", "estimated_audio_duration": 5 }}, ...]}}"""
            
            result, used_url = get_local_response(prompt)
            
            if result:
                try:
                    clean_json = result.replace('```json', '').replace('```', '').strip()
                    json.loads(clean_json)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(clean_json)
                    print(f"✅ SECURED")
                except:
                    print("♻️ Bad JSON")
            else:
                print("❌ OFFLINE OR 404")
            
if __name__ == "__main__":
    process_rescue()
