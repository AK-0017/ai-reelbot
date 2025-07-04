import os
from supabase import create_client
from session import get_current_session_folder

# === ENV from GitHub Secrets ===
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "reels"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Load current timestamp folder from session ===
folder = get_current_session_folder()
if not folder:
    raise Exception("❌ Timestamp session folder not found. Did you run fetch_latest_script.py first?")

# === Files to upload ===
FILES = {
    "final_reel.mp4": "temp/final_reel.mp4",
    "background.mp4": "temp/background.mp4",
    "music.mp3": "temp/music.mp3",
    "voiceover.mp3": "temp/voiceover.mp3",
}

print("☁️ Uploading final reel and assets to Supabase...")

for name, path in FILES.items():
    if not os.path.exists(path):
        print(f"⚠️ Skipping missing file: {path}")
        continue

    storage_path = f"{folder}/{name}"
    with open(path, "rb") as f:
        res = supabase.storage.from_(BUCKET_NAME).upload(
            storage_path, f, {"content-type": "video/mp4" if name.endswith(".mp4") else "audio/mpeg"}
        )
    
    if hasattr(res, "status_code") and res.status_code >= 400:
        print(f"❌ Failed to upload {name} → Status: {res.status_code}")
        print(res.json())
    else:
        print(f"✅ Uploaded: {storage_path}")

print("🎉 All available files uploaded to Supabase.")
