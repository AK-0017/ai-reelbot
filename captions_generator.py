# captions_generator.py 🎬
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, vfx
)

# === File paths ===
CHUNKS_METADATA = "temp/voiceover_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# === Caption Style ===
FONT = "Arial-Bold"
FONT_SIZE = 36
COLOR = "white"
SHADOW_COLOR = "black"
DURATION_PADDING = 0.3
CAPTION_MARGIN_BOTTOM = 120  # Adjust vertical position

def load_chunks_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_text(text):
    """Break long lines into two lines max (optional)."""
    if len(text) > 80:
        words = text.split()
        midpoint = len(words) // 2
        return " ".join(words[:midpoint]) + "\n" + " ".join(words[midpoint:])
    return text

def generate_caption_clips(metadata, video_size):
    clips = []

    for chunk in metadata:
        text = format_text(chunk["text"])
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start + DURATION_PADDING)

        txt = TextClip(
            text,
            fontsize=FONT_SIZE,
            font=FONT,
            color=COLOR,
            stroke_color=SHADOW_COLOR,
            stroke_width=2,
            size=(int(video_size[0] * 0.85), None),
            method="caption"
        )

        txt = txt.set_position(("center", video_size[1] - CAPTION_MARGIN_BOTTOM))
        txt = txt.set_start(start).set_duration(duration)

        # Add animation (fade + slight zoom)
        txt = txt.crossfadein(0.2).crossfadeout(0.2).fx(vfx.fadein, 0.2).fx(vfx.fadeout, 0.2)

        clips.append(txt)

    return clips

def render_video():
    print("🎥 Rendering final reel with styled captions...")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_chunks_metadata(CHUNKS_METADATA)

    caption_clips = generate_caption_clips(metadata, video.size)

    final_clip = CompositeVideoClip([video] + caption_clips)
    final_clip = final_clip.set_audio(audio).set_duration(audio.duration)

    final_clip.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)
    print(f"✅ Final reel saved as: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
