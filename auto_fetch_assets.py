# auto_fetch_assets.py ✅ FINAL VERSION
import os
import random
import requests
from supabase import create_client
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === CONFIG ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # ← set in GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_BUCKET = "background-music"
VIDEO_QUERY = [
    "futuristic", "technology", "cyberpunk", "ai", "data", "innovation",
    "digital", "tech", "smart", "robotics", "gadgets", "virtual reality",
    "augmented reality", "blockchain", "internet of things", "machine learning",
    "artificial intelligence", "smart home", "wearable tech", "5G", "quantum computing"
]
VIDEO_COUNT = 5

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === VIDEO FETCHING ===
def fetch_pexels_videos():
    print("🎥 Fetching tech-style vertical videos from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    all_clips = []

    for _ in range(20):
        query = random.choice(VIDEO_QUERY)
        try:
            res = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=medium&per_page=5",
                headers=headers
            )
            res.raise_for_status()
            data = res.json()
            for vid in data.get("videos", []):
                url = vid["video_files"][0]["link"]
                clip = VideoFileClip(url).resize(height=1080).crop(width=608, x_center=304).subclip(0, min(5, VideoFileClip(url).duration))
                all_clips.append(clip)
                if len(all_clips) >= VIDEO_COUNT:
                    break
        except Exception as e:
            print(f"⚠️ Failed to fetch or process video: {e}")

        if len(all_clips) >= VIDEO_COUNT:
            break

    return all_clips

def merge_videos(clips, output_path):
    print("🔗 Merging and resizing clips...")
    if not clips:
        raise Exception("❌ Not enough video clips to merge.")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=30)
    print(f"✅ Final merged video saved: {output_path}")

# === MUSIC FETCHING FROM SUPABASE BUCKET ===
def fetch_random_music(output_path):
    print("🎵 Fetching random music from Supabase...")
    try:
        files = supabase.storage.from_(SUPABASE_BUCKET).list("", {"limit": 100})
        files = [f["name"] for f in files if f["name"].endswith(".mp3")]

        if not files:
            raise Exception("❌ No music files found in Supabase bucket.")

        chosen = random.choice(files)
        print(f"🎯 Selected music: {chosen}")

        data = supabase.storage.from_(SUPABASE_BUCKET).download(chosen)
        with open(output_path, "wb") as f:
            f.write(data)

        print(f"✅ Music saved to: {output_path}")
    except Exception as e:
        print(f"❌ Music fetch failed: {e}")

# === MAIN RUN ===
if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    video_clips = fetch_pexels_videos()
    merge_videos(video_clips, output_path="temp/background.mp4")
    fetch_random_music(output_path="temp/music.mp3")
