# auto_fetch_assets.py ✅
import os
import random
import requests
import subprocess
import hashlib
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image

# 🔧 Pillow 10+ compatibility fix
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# === CONFIG ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # GitHub Secret
VIDEO_QUERY = [
    "futuristic", "technology", "cyberpunk", "ai", "data", "innovation",
    "digital", "tech", "smart", "robotics", "virtual reality", "machine learning"
]
VIDEO_COUNT = 5
USED_MUSIC_LOG = "used_music.txt"
TRIM_AUDIO = True
TRIM_START = "00:00:00"
TRIM_DURATION = "00:00:30"
TEMP_DIR = "temp"


# =============================
# 📥 Download and process video
# =============================
def download_video_file(url, path):
    r = requests.get(url, stream=True, timeout=15)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def fetch_pexels_videos():
    print("🎥 Fetching tech-style vertical videos from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    clips = []

    os.makedirs(TEMP_DIR, exist_ok=True)
    video_id = 0

    for _ in range(10):  # 10 tries
        query = random.choice(VIDEO_QUERY)
        try:
            res = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=medium&per_page=5",
                headers=headers,
                timeout=10
            )
            res.raise_for_status()
            data = res.json()

            for vid in data.get("videos", []):
                try:
                    video_url = vid["video_files"][0]["link"]
                    local_path = os.path.join(TEMP_DIR, f"video_{video_id}.mp4")
                    download_video_file(video_url, local_path)

                    clip = VideoFileClip(local_path).resize(height=1080).crop(width=608, x_center=304)
                    clip = clip.subclip(0, min(5, clip.duration))
                    clips.append(clip)
                    video_id += 1
                except Exception as e:
                    print(f"⚠️ Failed to process video clip: {e}")

                if len(clips) >= VIDEO_COUNT:
                    break
        except Exception as e:
            print(f"⚠️ Failed to fetch Pexels videos: {e}")

        if len(clips) >= VIDEO_COUNT:
            break

    return clips


# ====================
# 🎞️ Merge the videos
# ====================
def merge_videos(clips, output_path):
    print("🔗 Merging and resizing clips...")
    if not clips or len(clips) < 2:
        raise Exception("❌ Not enough video clips to merge.")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(output_path, fps=30, threads=4)
    print(f"✅ Final merged video saved: {output_path}")


# ===================
# 🎵 Download music
# ===================
def fetch_music(output_path):
    print("🎵 Downloading background music from YouTube using yt-dlp...")

    if not os.path.exists("music_sources.txt"):
        print("❌ music_sources.txt not found.")
        return

    with open("music_sources.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    used = set()
    if os.path.exists(USED_MUSIC_LOG):
        with open(USED_MUSIC_LOG, "r") as f:
            used = set(line.strip() for line in f)

    unused = [url for url in urls if hashlib.md5(url.encode()).hexdigest() not in used]

    if not unused:
        print("🔁 All music used once, resetting...")
        unused = urls
        os.remove(USED_MUSIC_LOG)

    for yt_url in unused:
        try:
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--output", output_path.replace(".mp3", ".%(ext)s")
            ]
            if TRIM_AUDIO:
                cmd += ["--postprocessor-args", f"ffmpeg:-ss {TRIM_START} -t {TRIM_DURATION}"]
            cmd.append(yt_url)
            subprocess.run(cmd, check=True)

            with open(USED_MUSIC_LOG, "a") as f:
                f.write(hashlib.md5(yt_url.encode()).hexdigest() + "\n")

            print(f"✅ Music downloaded and saved to: {output_path}")
            return
        except subprocess.CalledProcessError:
            print(f"⚠️ Skipping broken track: {yt_url}")
            continue

    print("❌ All music sources failed.")


# ============
# 🚀 Launcher
# ============
if __name__ == "__main__":
    os.makedirs(TEMP_DIR, exist_ok=True)

    video_clips = fetch_pexels_videos()
    merge_videos(video_clips, output_path=os.path.join(TEMP_DIR, "background.mp4"))
    fetch_music(output_path=os.path.join(TEMP_DIR, "music.mp3"))
