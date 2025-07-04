import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
VIDEO_PATH = "temp/final_video.mp4"
BUCKET_NAME = "final-reels"
OBJECT_NAME = os.path.basename(VIDEO_PATH)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment.")

if not os.path.exists(VIDEO_PATH):
    raise Exception(f"❌ Final video not found at {VIDEO_PATH}")

print("☁️ Uploading final reel to Supabase...")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "video/mp4",
    "x-upsert": "true"
}

with open(VIDEO_PATH, "rb") as f:
    data = f.read()

upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{OBJECT_NAME}"
res = requests.put(upload_url, headers=headers, data=data)

if res.status_code == 200:
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{OBJECT_NAME}"
    print(f"✅ Uploaded successfully. Public URL:\n{public_url}")
else:
    print(f"❌ Upload failed with status {res.status_code}:\n{res.text}")
