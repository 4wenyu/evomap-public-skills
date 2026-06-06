import os
import json
import glob
import re

SCRIPTS_DIR = "/home/taoai/taoai-empire/taoai-empire/EXPORTS/scripts"

def force_clean(text):
    if not text: return ""
    # 1. Strip LLM Prefix Junk ("脚本：", "Script:", "RULES:")
    text = re.sub(r'^(脚本|文案|台词|Script|Copy|Hook|Emotional Hook|RULES|MANDATE)[:：]?\s*', '', text, flags=re.IGNORECASE)
    # 2. Strip Markdown
    text = re.sub(r'^[\*\-#_—]+', '', text)
    return text.strip()

def is_phantom(text):
    # True if empty OR exactly a number like "1", "27.", "80"
    return text == "" or re.match(r'^\d+\.?$', text)

def sweep_sources():
    print("🧹 STARTING ULTIMATE SWEEPER: Force-cleaning 400+ JSON scripts...")
    files = glob.glob(os.path.join(SCRIPTS_DIR, "*.json"))
    cleaned_count = 0
    
    for file_path in files:
        if "TEST" in file_path: continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                continue
        
        scenes = data.get("scenes", [])
        if not scenes: continue
        
        valid_scenes = []
        for s in scenes:
            # Clean the text to remove "脚本："
            s["spoken_text"] = force_clean(s.get("spoken_text", ""))
            
            # If it's a phantom number and NOT the hook, drop it
            if is_phantom(s["spoken_text"]) and s.get("scene_type") != "HOOK_LTX":
                continue
            valid_scenes.append(s)
            
        # HOOK ENFORCER: If Scene 1 is empty or a phantom number ("27."), pull text from Scene 2
        if valid_scenes and is_phantom(valid_scenes[0].get("spoken_text", "")):
            if len(valid_scenes) > 1:
                valid_scenes[0]["spoken_text"] = valid_scenes[1]["spoken_text"]
                
        # LTX PARAMETER ENFORCER
        if valid_scenes and valid_scenes[0].get("scene_type") == "HOOK_LTX":
            valid_scenes[0]["visual_asset"] = "PENDING_LTX_GENERATION"
            vp = valid_scenes[0].get("visual_prompt", "")
            if "9:16" not in vp:
                valid_scenes[0]["visual_prompt"] = vp.strip() + ", Vertical 9:16, HD, 30fps"
                
        # Renumber correctly
        for idx, s in enumerate(valid_scenes):
            s["scene_number"] = idx + 1
            
        data["scenes"] = valid_scenes
        
        # ABSOLUTE OVERWRITE
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        cleaned_count += 1
            
    print(f"✅ ULTIMATE SWEEP COMPLETE! {cleaned_count} files scrubbed, sanitized, and forcefully overwritten.")

if __name__ == "__main__":
    sweep_sources()
