import os
import random
import requests
import subprocess
import hashlib
import uuid
from supabase import create_client
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === CONFIG ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # Use GitHub secret
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "background-music"
MUSIC_FILENAMES = ["1.mp3", "2.mp3", "3.mp3", "4.mp3", "5.mp3"]
VIDEO_QUERY = [
    "futuristic", "technology", "cyberpunk", "ai", "data", "innovation",
    "digital", "tech", "smart", "robotics", "gadgets", "virtual reality",
    "augmented reality", "blockchain", "internet of things", "machine learning",
    "artificial intelligence", "smart home", "wearable tech", "5G", "quantum computing"
]
VIDEO_COUNT = 5

# === INIT ===
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
os.makedirs("temp", exist_ok=True)


def fetch_pexels_videos():
    print("🎥 Fetching tech-style vertical videos from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    all_clips = []

    for _ in range(20):  # Try up to 20 videos
        query = random.choice(VIDEO_QUERY)
        try:
            res = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=medium&per_page=5",
                headers=headers
            )
            res.raise_for_status()
            data = res.json()

            for vid in data.get("videos", []):
                video_url = vid["video_files"][0]["link"]
                temp_path = f"temp/{uuid.uuid4()}.mp4"

                # Download video locally first
                with open(temp_path, "wb") as f:
                    f.write(requests.get(video_url).content)

                # Then load locally into MoviePy
                clip = (
                    VideoFileClip(temp_path)
                    .resize(height=1080)
                    .crop(width=608, x_center=304)
                    .subclip(0, min(5, VideoFileClip(temp_path).duration))
                )
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
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")
    print(f"✅ Final merged video saved: {output_path}")


def fetch_random_music(output_path):
    print("🎵 Fetching random background music from Supabase...")

    filename = random.choice(MUSIC_FILENAMES)
    try:
        file_data = supabase.storage.from_(BUCKET_NAME).download(filename)
        with open(output_path, "wb") as f:
            f.write(file_data)
        print(f"✅ Music downloaded and saved to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to download music '{filename}' from Supabase: {e}")


if __name__ == "__main__":
    video_clips = fetch_pexels_videos()
    merge_videos(video_clips, output_path="temp/background.mp4")
    fetch_random_music(output_path="temp/music.mp3")
