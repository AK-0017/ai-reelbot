# captions_generator.py 🎬 FINAL v9 — Polished Captions + Box Fix + End Glitch Fix
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, ColorClip
)
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.video.fx import fadein, fadeout, resize

# === File Paths ===
CAPTIONS_METADATA = "temp/caption_chunks.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"
MUSIC_FILE = "temp/music.mp3"

# === Caption Style ===
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 50
TEXT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 3
CAPTION_WIDTH_RATIO = 0.85
MAX_WORDS_PER_LINE = 6
CAPTION_FADE_DURATION = 0.3
CAPTION_SCALE_START = 0.95
CAPTION_SCALE_END = 1.0
CAPTION_CENTER_HEIGHT = 0.55

# === Overlay & Background ===
BACKGROUND_OPACITY = 0.4
GRADIENT_OPACITY = 0.2
BACKGROUND_HEIGHT = FONT_SIZE * 2

# === Progress Bar ===
PROGRESS_HEIGHT = 8
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
        font=FONT_PATH,
        color=TEXT_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
        method="caption",
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), None)
    )
    y_pos = int(video_size[1] * CAPTION_CENTER_HEIGHT) - caption.h // 2
    caption = caption.set_position(("center", y_pos)).set_start(start).set_duration(duration)
    caption = caption.fx(resize.resize, CAPTION_SCALE_START).fx(
        resize.resize, lambda t: CAPTION_SCALE_START + (CAPTION_SCALE_END - CAPTION_SCALE_START) * min(t / duration, 1)
    )
    return fadeout.fadeout(fadein.fadein(caption, CAPTION_FADE_DURATION), CAPTION_FADE_DURATION)


def create_background_box(start, duration, video_size, lines=2):
    if lines < 2:
        return None  # Show only for multiline captions
    box = ColorClip(
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), BACKGROUND_HEIGHT),
        color=(0, 0, 0)
    ).set_opacity(BACKGROUND_OPACITY)
    y_pos = int(video_size[1] * CAPTION_CENTER_HEIGHT) - BACKGROUND_HEIGHT // 2
    return box.set_position(("center", y_pos)).set_start(start).set_duration(duration)


def create_progress_bar(duration, video_size):
    bar = ColorClip(size=(1, PROGRESS_HEIGHT), color=PROGRESS_COLOR)
    animated_bar = bar.resize(lambda t: (max(2, int(video_size[0] * (t / duration))), PROGRESS_HEIGHT))
    return animated_bar.set_position(("left", video_size[1] - PROGRESS_HEIGHT)).set_duration(duration)


def create_gradient_overlay(video_size, duration):
    return ColorClip(size=video_size, color=(0, 0, 0)).set_opacity(GRADIENT_OPACITY).set_duration(duration)


def generate_all_layers(metadata, video_size, total_duration):
    caption_clips = []
    overlays = []

    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start)

        caption = create_caption_clip(text, start, duration, video_size)
        lines = caption.txt.count("\n") + 1

        caption_clips.append(caption)

        box = create_background_box(start, duration, video_size, lines=lines)
        if box:
            overlays.append(box)

    progress = create_progress_bar(total_duration, video_size)
    gradient = create_gradient_overlay(video_size, total_duration)

    return caption_clips + overlays + [progress, gradient]


def render_video():
    print("🎬 Rendering FINAL v9 — Polished Captions + Music + No Glitch...")

    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError("❌ Background video missing.")
    if not os.path.exists(VOICEOVER_FILE):
        raise FileNotFoundError("❌ Voiceover missing.")
    if not os.path.exists(CAPTIONS_METADATA):
        raise FileNotFoundError("❌ Caption metadata missing.")

    video = VideoFileClip(INPUT_VIDEO)
    voiceover = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CAPTIONS_METADATA)

    # 🎵 Music overlay
    if os.path.exists(MUSIC_FILE):
        print("🎵 Adding music (fade-in/out)...")
        music = AudioFileClip(MUSIC_FILE).volumex(0.15).audio_fadein(2).audio_fadeout(2)
        final_audio = CompositeAudioClip([music, voiceover])
    else:
        final_audio = voiceover

    # 🎬 Match duration and prevent glitch
    final_duration = min(voiceover.duration, video.duration)
    video = video.subclip(0, final_duration).fadeout(1)
    layers = generate_all_layers(metadata, video.size, final_duration)

    final = CompositeVideoClip([video] + layers).set_audio(final_audio.set_duration(final_duration))
    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)

    print(f"✅ Final cinematic reel saved: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    render_video()
