# captions_generator.py 🎬 ULTIMATE REEL EDITION BY ChatGPT
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, ColorClip
)
from moviepy.video.fx import fadein, fadeout, resize
from moviepy.video.tools.drawing import color_gradient

# === File Paths ===
CHUNKS_METADATA = "temp/voiceover_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# === Caption Style Settings ===
FONT = "Arial-Bold"
FONT_SIZE = 48
CAPTION_WIDTH_RATIO = 0.85
TEXT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 2
FADE_DURATION = 0.3
BACKGROUND_OPACITY = 0.4
MAX_WORDS_PER_LINE = 8

# === Animation Settings ===
SCALE_START = 0.92  # Zoom-in animation
SCALE_END = 1.0

# === Progress Bar Settings ===
PROGRESS_HEIGHT = 10
PROGRESS_COLOR = (255, 255, 255)


def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_text(text):
    words = text.strip().split()
    if len(words) <= MAX_WORDS_PER_LINE:
        return text
    midpoint = len(words) // 2
    return " ".join(words[:midpoint]) + "\n" + " ".join(words[midpoint:])

def create_caption_clip(text, start, duration, video_size):
    formatted_text = format_text(text)

    caption = TextClip(
        formatted_text,
        fontsize=FONT_SIZE,
        font=FONT,
        color=TEXT_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
        method="caption",
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), None)
    )

    # Start small and scale up
    caption = caption.set_position("center").set_start(start).set_duration(duration)
    caption = caption.fx(resize.resize, SCALE_START).fx(resize.resize, lambda t: SCALE_START + (SCALE_END - SCALE_START) * min(t / duration, 1))
    caption = fadein.fadein(caption, FADE_DURATION)
    caption = fadeout.fadeout(caption, FADE_DURATION)

    return caption

def create_background_overlay(start, duration, video_size):
    overlay = ColorClip(
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), FONT_SIZE * 2),
        color=(0, 0, 0)
    ).set_opacity(BACKGROUND_OPACITY)

    overlay = overlay.set_position("center")
    overlay = overlay.set_start(start).set_duration(duration)

    return overlay

def create_progress_bar(duration, video_size):
    bar = ColorClip(
        size=(1, PROGRESS_HEIGHT),
        color=PROGRESS_COLOR
    ).set_position(("left", video_size[1] - PROGRESS_HEIGHT))

    animated_bar = bar.resize(lambda t: (max(2, int(video_size[0] * (t / duration))), PROGRESS_HEIGHT))

    return animated_bar.set_duration(duration)

def generate_gradient_overlay(video_size, duration):
    gradient = ColorClip(
        size=video_size,
        color=(0, 0, 0)
    ).set_opacity(0.2)
    return gradient.set_duration(duration)

def generate_all_layers(metadata, video_size, total_duration):
    caption_clips = []
    overlays = []

    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start)

        caption_clip = create_caption_clip(text, start, duration, video_size)
        bg_overlay = create_background_overlay(start, duration, video_size)

        caption_clips.append(caption_clip)
        overlays.append(bg_overlay)

    progress = create_progress_bar(total_duration, video_size)
    gradient_layer = generate_gradient_overlay(video_size, total_duration)
    return caption_clips + overlays + [progress, gradient_layer]

def render_video():
    print("🎬 Rendering ChatGPT-Ultimate Reel with cinematic edits...")

    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError(f"❌ Background video missing: {INPUT_VIDEO}")
    if not os.path.exists(VOICEOVER_FILE):
        raise FileNotFoundError(f"❌ Voiceover audio missing: {VOICEOVER_FILE}")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CHUNKS_METADATA)

    video = video.set_duration(audio.duration)
    overlays = generate_all_layers(metadata, video.size, audio.duration)

    final = CompositeVideoClip([video] + overlays).set_audio(audio)
    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)

    print(f"✅ Final cinematic reel saved: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
