import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 1. SETUP
BASE_DIR = Path('/home/taoai/taoai-empire/taoai-empire')
load_dotenv(BASE_DIR / '.env')
RAW_INPUTS_DIR = BASE_DIR / 'ASSETS/RAW_INPUTS'
EXPORTS_DIR = BASE_DIR / 'EXPORTS'
SCRIPTS_DIR = EXPORTS_DIR / "scripts"

client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.getenv("NVIDIA_API_KEY"))
MODEL_ID = "meta/llama-3.1-70b-instruct"

def force_clean(text):
    if not text: return ""
    text = re.sub(r'^(脚本|文案|台词|Script|Copy|Hook|Emotional Hook|RULES|MANDATE)[:：]?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^[\*\-#_—]+', '', text)
    return text.strip()

def process_scripts():
    print("🚀 STARTING FLAWLESS SCRIPT ENGINE: FULL PRODUCTION RUN...")
    with open(EXPORTS_DIR / "master_video_metadata.json", 'r') as f:
        catalog = json.load(f).get('visuals', [])
        catalog_str = " | ".join([i['id'] for i in catalog if i.get('id')])

    targets = [
        {"file": "hooks_short_en.md", "prefix": "short_en", "dur": "7s"},
        {"file": "hooks_short_cn.md", "prefix": "short_cn", "dur": "7s"},
        {"file": "hooks_vlog_en.md", "prefix": "vlog_en", "dur": "35-55s"},
        {"file": "hooks_vlog_cn.md", "prefix": "vlog_cn", "dur": "35-55s"}
    ]

    for t in targets:
        f_path = RAW_INPUTS_DIR / t["file"]
        if not f_path.exists(): continue
        
        with open(f_path, 'r', encoding='utf-8') as f:
            content_raw = f.read()
            raw_scripts = [s.strip() for s in content_raw.split('---') if len(s.strip()) > 10] if 'short' in t['prefix'] else re.split(r'\n(?=\s*\d+\.\s*[【\[])', content_raw)
            raw_scripts = [s.strip() for s in raw_scripts if len(s.strip()) > 20]

        for idx, content in enumerate(raw_scripts):
            sid = f"{t['prefix']}_{idx+1:03d}"
            out_file = SCRIPTS_DIR / f"{sid}.json"

            prompt = (
                f"You are a strict data processor. Process this text: {content}\n\n"
                f"RULES:\n"
                f"1. Extract the most viral 'Golden-3-seconds' hook from the text and place it in Scene 1.\n"
                f"2. Split the remaining text into subsequent scenes.\n"
                f"3. Scene 1 visual_prompt MUST end with: 'Vertical 9:16, HD, 30fps'.\n"
                f"4. Assign a B-Roll ID from this list ONLY: {catalog_str}\n"
                f"5. YOU MUST USE THIS EXACT JSON FORMAT. DO NOT CHANGE THE KEYS:\n"
                f"{{\n"
                f"  \"script_id\": \"{sid}\",\n"
                f"  \"scenes\": [\n"
                f"    {{\n"
                f"      \"scene_number\": 1,\n"
                f"      \"scene_type\": \"HOOK_LTX\",\n"
                f"      \"visual_asset\": \"PENDING_LTX_GENERATION\",\n"
                f"      \"visual_prompt\": \"[Cinematic description here], Vertical 9:16, HD, 30fps\",\n"
                f"      \"spoken_text\": \"[Golden Hook Here]\",\n"
                f"      \"estimated_audio_duration\": 3\n"
                f"    }},\n"
                f"    {{\n"
                f"      \"scene_number\": 2,\n"
                f"      \"scene_type\": \"SPEECH\",\n"
                f"      \"visual_asset\": \"[B-ROLL ID HERE]\",\n"
                f"      \"spoken_text\": \"[Next sentence here]\"\n"
                f"    }}\n"
                f"  ]\n"
                f"}}\n"
                f"OUTPUT ONLY VALID JSON."
            )

            try:
                response = client.chat.completions.create(model=MODEL_ID, messages=[{"role": "user", "content": prompt}], temperature=0.0)
                res_text = response.choices[0].message.content
                json_str = res_text[res_text.find('{'):res_text.rfind('}')+1]
                data = json.loads(json_str)
                
                scenes = data.get("scenes", [])
                for s in scenes:
                    s["spoken_text"] = force_clean(s.get("spoken_text", s.get("text", s.get("script", ""))))
                    raw_asset = s.get("visual_asset", s.get("visual_prompt", "VIDEO_6411"))
                    if s.get("scene_type") == "HOOK_LTX" or "PENDING" in raw_asset.upper():
                        s["visual_asset"] = "PENDING_LTX_GENERATION"
                    else:
                        s["visual_asset"] = raw_asset[:10]
                
                # Phantom check on new logic
                if scenes and (not scenes[0]["spoken_text"] or re.match(r'^\d+\.?$', scenes[0]["spoken_text"])) and len(scenes) > 1:
                     scenes[0]["spoken_text"] = scenes[1]["spoken_text"]

                data["scenes"] = [s for s in scenes if s["spoken_text"] != "" and not (re.match(r'^\d+\.?$', s["spoken_text"]) and s["scene_type"] != "HOOK_LTX")]
                
                # 🛑 THE NEW ENFORCEMENT GUARDRAIL 🛑
                if not data["scenes"]:
                    raise ValueError("LLM generated an empty array. Aborting save.")
                    
                with open(out_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✅ {sid} | SAVED FOR PRODUCTION")
            except Exception as e:
                print(f"❌ {sid} | Failed: {str(e)}")

if __name__ == "__main__":
    process_scripts()
