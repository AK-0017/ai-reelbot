# captions_generator.py 🎬 (Upgraded & Aesthetic)
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

# === Caption Settings ===
FONT = "Arial-Bold"
FONT_SIZE = 38
TEXT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 2
BOTTOM_MARGIN = 120
FADE_DURATION = 0.3

def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_text(text, max_words=8):
    words = text.split()
    if len(words) <= max_words:
        return text
    return "\n".join([" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)])

def create_caption_clips(metadata, video_size):
    clips = []
    for chunk in metadata:
        text = format_text(chunk["text"])
        start, end = chunk["start"], chunk["end"]
        duration = max(0.5, end - start)

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
            .set_position(("center", video_size[1] - BOTTOM_MARGIN))
            .set_start(start)
            .set_duration(duration)
            .crossfadein(FADE_DURATION)
            .crossfadeout(FADE_DURATION)
        )
        clips.append(caption)
    return clips

def render_video():
    print("🎥 Rendering modern styled reel...")
    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CHUNKS_METADATA)

    captions = create_caption_clips(metadata, video.size)
    final = CompositeVideoClip([video] + captions)
    final = final.set_audio(audio).set_duration(audio.duration)

    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)
    print(f"✅ Final reel saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
