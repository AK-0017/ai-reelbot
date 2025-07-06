# captions_generator.py 🎬 FINAL v11 — Clean + Slide captions + Zoomed video + Music loop
import os
import json
from moviepy.editor import (
    VideoFileClip, TextClip, CompositeVideoClip,
    AudioFileClip, ColorClip, vfx
)
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.fx.all import audio_loop
from moviepy.video.fx import fadein, fadeout

# === File Paths ===
CAPTIONS_METADATA = "temp/caption_chunks.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"
MUSIC_FILE = "temp/music.mp3"
FONT_PATH = "fonts/Inter-Bold.ttf"

# === Style ===
FONT_SIZE = 52
TEXT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 3
CAPTION_WIDTH_RATIO = 0.9
CAPTION_FADE_DURATION = 0.3
CAPTION_CENTER_HEIGHT = 0.55
PROGRESS_HEIGHT = 8
PROGRESS_COLOR = (255, 255, 255)
GRADIENT_OPACITY = 0.15


def load_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_text(text):
    words = text.strip().split()
    if len(words) <= 6:
        return text
    midpoint = len(words) // 2
    return " ".join(words[:midpoint]) + "\n" + " ".join(words[midpoint:])


def create_caption_clip(text, start, duration, video_size):
    formatted = format_text(text)
    caption = TextClip(
        formatted,
        fontsize=FONT_SIZE,
        font=FONT_PATH,
        color=TEXT_COLOR,
        stroke_color=STROKE_COLOR,
        stroke_width=STROKE_WIDTH,
        method="caption",
        size=(int(video_size[0] * CAPTION_WIDTH_RATIO), None)
    )
    y = int(video_size[1] * CAPTION_CENTER_HEIGHT) - caption.h // 2
    caption = caption.set_position(lambda t: ("center", y + 20 - 20 * min(t / 0.4, 1)))
    caption = caption.set_start(start).set_duration(duration)
    caption = fadein.fadein(caption, CAPTION_FADE_DURATION)
    caption = fadeout.fadeout(caption, CAPTION_FADE_DURATION)
    return caption


def create_progress_bar(duration, video_size):
    bar = ColorClip(size=(1, PROGRESS_HEIGHT), color=PROGRESS_COLOR)
    animated = bar.resize(lambda t: (max(2, int(video_size[0] * (t / duration))), PROGRESS_HEIGHT))
    return animated.set_position(("left", video_size[1] - PROGRESS_HEIGHT)).set_duration(duration)


def create_gradient_overlay(video_size, duration):
    gradient = ColorClip(size=video_size, color=(0, 0, 0)).set_opacity(GRADIENT_OPACITY)
    return gradient.set_duration(duration)


def generate_all_layers(metadata, video_size, total_duration):
    layers = []
    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start)
        caption = create_caption_clip(text, start, duration, video_size)
        layers.append(caption)

    layers.append(create_progress_bar(total_duration, video_size))
    layers.append(create_gradient_overlay(video_size, total_duration))
    return layers


def render_video():
    print("🎬 Rendering FINAL v11 — Slide-up captions, looping background/music...")

    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError("❌ Background video missing.")
    if not os.path.exists(VOICEOVER_FILE):
        raise FileNotFoundError("❌ Voiceover missing.")
    if not os.path.exists(CAPTIONS_METADATA):
        raise FileNotFoundError("❌ Caption metadata missing.")

    voiceover = AudioFileClip(VOICEOVER_FILE)
    caption_metadata = load_metadata(CAPTIONS_METADATA)

    # 🔁 Loop & zoom video
    bg_clip = VideoFileClip(INPUT_VIDEO)
    if bg_clip.duration < voiceover.duration:
        print("🔁 Looping background video...")
        loops_needed = int(voiceover.duration // bg_clip.duration) + 1
        clips = [bg_clip] * loops_needed
        bg_clip = concatenate_videoclips(clips).subclip(0, voiceover.duration)
    bg_clip = bg_clip.fx(vfx.crop, x_center=bg_clip.w/2, width=bg_clip.w*0.95)
    bg_clip = bg_clip.fx(vfx.resize, height=1080)
    bg_clip = bg_clip.set_duration(voiceover.duration)

    # 🔁 Loop background music
    if os.path.exists(MUSIC_FILE):
        print("🎵 Adding looping music...")
        music_clip = AudioFileClip(MUSIC_FILE).volumex(0.15)
        music_full = audio_loop(music_clip, duration=voiceover.duration).subclip(0, voiceover.duration)
        music_faded = music_full.audio_fadein(2).audio_fadeout(2)
        final_audio = CompositeAudioClip([music_faded, voiceover])
    else:
        print("⚠️ No music file found, using voiceover only.")
        final_audio = voiceover

    layers = generate_all_layers(caption_metadata, bg_clip.size, voiceover.duration)
    final = CompositeVideoClip([bg_clip] + layers).set_audio(final_audio)
    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)

    print(f"✅ Final cinematic reel saved: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    render_video()
