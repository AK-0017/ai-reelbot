# captions_generator.py 🎬
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip
)

# === Paths ===
INPUT_VIDEO = "temp/background.mp4"
VOICEOVER_FILE = "temp/voiceover.mp3"
CHUNKS_METADATA = "temp/voiceover_metadata.json"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# === Style Config ===
FONT = "Arial-Bold"
FONT_SIZE = 44
TEXT_COLOR = "white"
STROKE_COLOR = "black"
BOTTOM_MARGIN = 160
FADE_DURATION = 0.3

def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def split_lines(text, max_words=8):
    """Break long sentences into 2 lines max."""
    words = text.split()
    if len(words) <= max_words:
        return text
    mid = len(words) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

def generate_captions(metadata, video_size):
    clips = []

    for i, chunk in enumerate(metadata):
        text = split_lines(chunk["text"])
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start)

        clip = (
            TextClip(
                text,
                fontsize=FONT_SIZE,
                font=FONT,
                color=TEXT_COLOR,
                stroke_color=STROKE_COLOR,
                stroke_width=2,
                size=(int(video_size[0] * 0.85), None),
                method="caption"
            )
            .set_position(("center", video_size[1] - BOTTOM_MARGIN))
            .set_start(start)
            .set_duration(duration)
            .fadein(FADE_DURATION)
            .fadeout(FADE_DURATION)
        )
        clips.append(clip)

    return clips

def render_video():
    print("🎬 Rendering video with animated captions...")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CHUNKS_METADATA)

    caption_clips = generate_captions(metadata, video.size)
    final = CompositeVideoClip([video] + caption_clips)
    final = final.set_audio(audio).set_duration(audio.duration)

    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)
    print(f"✅ Final reel saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
