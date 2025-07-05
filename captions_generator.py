# captions_generator.py 🎬 FINAL FIXED VERSION
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, vfx
)

# === Paths ===
CHUNKS_METADATA = "temp/voiceover_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# === Caption Style ===
FONT = "Arial-Bold"
FONT_SIZE = 38
TEXT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 2
FADE_DURATION = 0.3
MAX_WORDS_PER_LINE = 8

def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_text(text):
    words = text.split()
    if len(words) <= MAX_WORDS_PER_LINE:
        return text
    mid = len(words) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])

def generate_caption_clips(metadata, video_size):
    clips = []
    for chunk in metadata:
        text = format_text(chunk["text"])
        start, end = chunk["start"], chunk["end"]
        duration = max(0.5, end - start)

        # Create styled animated caption
        caption = (
            TextClip(
                text,
                fontsize=FONT_SIZE,
                font=FONT,
                color=TEXT_COLOR,
                stroke_color=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
                size=(int(video_size[0] * 0.85), None),
                method="caption"
            )
            .set_position(("center", "bottom"))
            .set_start(start)
            .set_duration(duration)
            .fadein(FADE_DURATION)
            .fadeout(FADE_DURATION)
        )
        clips.append(caption)
    return clips

def render_video():
    print("🎥 Rendering your final reel with synced animated captions...")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CHUNKS_METADATA)

    captions = generate_caption_clips(metadata, video.size)

    # ⛔ Important: make video shorter or match to audio duration
    final = CompositeVideoClip([video.set_duration(audio.duration)] + captions)
    final = final.set_audio(audio)

    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)
    print(f"✅ Final exported: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
