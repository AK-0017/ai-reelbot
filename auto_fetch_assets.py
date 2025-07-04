import os
import random
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === CONFIG ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
SUPABASE_MUSIC_BASE_URL = os.environ.get("SUPABASE_MUSIC_BASE_URL")  # Format: https://xxx.supabase.co/storage/v1/object/public/background-music
VIDEO_QUERY = [
    "futuristic", "technology", "cyberpunk", "ai", "data", "innovation",
    "digital", "tech", "robotics", "smart home", "wearable tech", "5G", "quantum computing"
]
VIDEO_COUNT = 5
MUSIC_OPTIONS = ["1.mp3", "2.mp3", "3.mp3", "4.mp3", "5.mp3"]


def fetch_pexels_videos(download_dir="temp"):
    print("🎥 Fetching tech-style vertical videos from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    os.makedirs(download_dir, exist_ok=True)
    downloaded = []

    for attempt in range(10):
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
                index = len(downloaded)
                local_path = os.path.join(download_dir, f"video_{index}.mp4")

                # Download video to file
                video_bytes = requests.get(url).content
                with open(local_path, "wb") as f:
                    f.write(video_bytes)

                # Load + preprocess clip
                clip = VideoFileClip(local_path)
                trimmed = clip.resize(height=1080).crop(width=608, x_center=304).subclip(0, min(5, clip.duration))
                downloaded.append(trimmed)

                if len(downloaded) >= VIDEO_COUNT:
                    return downloaded

        except Exception as e:
            print(f"⚠️ Failed to fetch or process video: {e}")

    return downloaded


def merge_videos(clips, output_path):
    if not clips:
        raise Exception("❌ Not enough video clips to merge.")
    print("🔗 Merging and rendering video clips...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=30, audio=False)
    print(f"✅ Final background video saved: {output_path}")


def fetch_random_music(output_path="temp/music.mp3"):
    print("🎵 Fetching background music from Supabase...")

    music_file = random.choice(MUSIC_OPTIONS)
    track_url = f"{SUPABASE_MUSIC_BASE_URL}/{music_file}"

    try:
        response = requests.get(track_url)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Music downloaded and saved to: {output_path}")
    except Exception as e:
        raise Exception(f"❌ Failed to fetch background music: {e}")


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)

    video_clips = fetch_pexels_videos(download_dir="temp")
    merge_videos(video_clips, output_path="temp/background.mp4")
    fetch_random_music(output_path="temp/music.mp3")
