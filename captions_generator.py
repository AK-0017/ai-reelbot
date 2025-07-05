# captions_generator.py 🎬 ULTIMATE REEL EDITION v4 — Split Captions + Sentence Voiceover
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, ColorClip
)
from moviepy.video.fx import fadein, fadeout, resize

# === File Paths ===
CHUNKS_METADATA = "temp/voiceover_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

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


def split_text_into_chunks(text, max_words=6):
    words = text.strip().split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def create_caption_clip(text, start, duration, video_size):
    caption = TextClip(
        text,
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
    caption = fadein.fadein(caption, CAPTION_FADE_DURATION)
    caption = fadeout.fadeout(caption, CAPTION_FADE_DURATION)

    return caption


def create_background_box(start, duration, video_size):
    box = ColorClip(
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), BACKGROUND_HEIGHT),
        color=(0, 0, 0)
    ).set_opacity(BACKGROUND_OPACITY)

    y_pos = int(video_size[1] * CAPTION_CENTER_HEIGHT) - BACKGROUND_HEIGHT // 2
    return box.set_position(("center", y_pos)).set_start(start).set_duration(duration)


def create_progress_bar(duration, video_size):
    bar = ColorClip(
        size=(1, PROGRESS_HEIGHT),
        color=PROGRESS_COLOR
    ).set_position(("left", video_size[1] - PROGRESS_HEIGHT))

    animated_bar = bar.resize(lambda t: (max(2, int(video_size[0] * (t / duration))), PROGRESS_HEIGHT))
    return animated_bar.set_duration(duration)


def create_gradient_overlay(video_size, duration):
    gradient = ColorClip(size=video_size, color=(0, 0, 0)).set_opacity(GRADIENT_OPACITY)
    return gradient.set_duration(duration)


def generate_all_layers(metadata, video_size, total_duration):
    caption_clips = []
    overlays = []

    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start)

        sub_chunks = split_text_into_chunks(text, MAX_WORDS_PER_LINE)
        per_chunk_duration = duration / len(sub_chunks)

        for i, part in enumerate(sub_chunks):
            sub_start = start + i * per_chunk_duration
            sub_caption = create_caption_clip(part, sub_start, per_chunk_duration, video_size)
            bg = create_background_box(sub_start, per_chunk_duration, video_size)

            caption_clips.append(sub_caption)
            overlays.append(bg)

    progress = create_progress_bar(total_duration, video_size)
    gradient = create_gradient_overlay(video_size, total_duration)

    return caption_clips + overlays + [progress, gradient]


def render_video():
    print("🎬 Rendering ULTIMATE REEL v4 — smooth voice + smart captions...")

    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError(f"❌ Background video missing: {INPUT_VIDEO}")
    if not os.path.exists(VOICEOVER_FILE):
        raise FileNotFoundError(f"❌ Voiceover missing: {VOICEOVER_FILE}")
    if not os.path.exists(CHUNKS_METADATA):
        raise FileNotFoundError(f"❌ Metadata missing: {CHUNKS_METADATA}")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_metadata(CHUNKS_METADATA)

    video = video.set_duration(audio.duration)
    layers = generate_all_layers(metadata, video.size, audio.duration)

    final = CompositeVideoClip([video] + layers).set_audio(audio)
    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)

    print(f"✅ Final cinematic reel saved: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    render_video()