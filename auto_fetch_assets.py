import os
import random
import requests
import subprocess
import hashlib
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === CONFIG ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")  # GitHub Secret
VIDEO_QUERY = [
    "futuristic", "technology", "cyberpunk", "ai", "data", "innovation",
    "digital", "tech", "robotics", "smart home", "wearable tech", "5G", "quantum computing"
]
VIDEO_COUNT = 5
USED_MUSIC_LOG = "used_music.txt"
TRIM_AUDIO = True
TRIM_START = "00:00:00"
TRIM_DURATION = "00:00:30"

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


def fetch_music(output_path):
    print("🎵 Downloading music from YouTube using yt-dlp...")

    if not os.path.exists("music_sources.txt"):
        raise Exception("❌ music_sources.txt is missing.")

    with open("music_sources.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    used = set()
    if os.path.exists(USED_MUSIC_LOG):
        with open(USED_MUSIC_LOG, "r") as f:
            used = set(line.strip() for line in f)

    unused = [url for url in urls if hashlib.md5(url.encode()).hexdigest() not in used]
    if not unused:
        print("🔁 All music used once. Resetting log.")
        unused = urls
        os.remove(USED_MUSIC_LOG)

    for url in unused:
        try:
            cmd = [
                "yt-dlp",
                "--no-playlist",
                "--extract-audio",
                "--audio-format", "mp3",
                "--quiet",
                "--output", output_path.replace(".mp3", ".%(ext)s")
            ]
            if TRIM_AUDIO:
                cmd += ["--postprocessor-args", f"ffmpeg:-ss {TRIM_START} -t {TRIM_DURATION}"]
            cmd.append(url)

            subprocess.run(cmd, check=True)
            with open(USED_MUSIC_LOG, "a") as f:
                f.write(hashlib.md5(url.encode()).hexdigest() + "\n")
            print(f"✅ Music downloaded and saved to: {output_path}")
            return
        except subprocess.CalledProcessError:
            print(f"⚠️ Skipping broken track: {url}")
            continue

    raise Exception("❌ All music sources failed.")


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)

    video_clips = fetch_pexels_videos(download_dir="temp")
    merge_videos(video_clips, output_path="temp/background.mp4")
    fetch_music(output_path="temp/music.mp3")
