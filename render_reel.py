import os
import numpy as np
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClip, CompositeAudioClip
)
from moviepy.video.fx.all import crop
from moviepy.video.VideoClip import VideoClip

# === CONFIG ===
MAX_DURATION = 30
SCRIPT_PATH = "temp/single_script.txt"
VOICE_PATH = "temp/voiceover.mp3"
MUSIC_PATH = "temp/music.mp3"
BACKGROUND_PATH = "temp/background.mp4"
OUTPUT_PATH = "temp/final_reel.mp4"
LOGO_PATH = "assets/logo.png"

# === Load Script ===
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = [line.strip() for line in f if line.strip()]

# === Load Clips ===
voice = AudioFileClip(VOICE_PATH)
music = AudioFileClip(MUSIC_PATH)
bg = VideoFileClip(BACKGROUND_PATH)

# === Duration sync ===
final_duration = min(MAX_DURATION, voice.duration, music.duration, bg.duration)
print(f"🎯 Final reel duration: {final_duration:.2f} seconds")

# === Prepare audio ===
voice = voice.subclip(0, final_duration).audio_fadein(1).audio_fadeout(1)
music = music.subclip(0, final_duration).volumex(0.2).audio_fadein(1).audio_fadeout(1)
final_audio = CompositeAudioClip([music, voice])

# === Background video with zoom ===
bg = bg.subclip(0, final_duration)
bg = crop(bg.resize(width=720), width=720, height=1280)
bg = bg.resize(lambda t: 1 + 0.02 * t)  # zoom effect

# === Glass panel overlay ===
glass = ColorClip((720, 460), (0, 0, 0)).set_opacity(0.4).set_duration(final_duration).set_position(("center", 400))

# === Animated text ===
def anim_text(txt, y, start, size=48, dur=4):
    return (
        TextClip(txt, fontsize=size, color="white", font="Arial-Bold", method="caption", size=(660, None))
        .set_duration(dur).set_start(start)
        .set_position(("center", y))
        .crossfadein(0.5).crossfadeout(0.4)
    )

texts = []
start_time = 1
y = 410
for i, line in enumerate(script[:6]):
    texts.append(anim_text(line, y + i * 60, start_time + i * 2, size=52 if i == 0 else 48))

# === CTA ===
cta = anim_text("📲 Follow for daily AI updates!", 1180, final_duration - 4, size=42)
texts.append(cta)

# === Logo watermark ===
logo = None
if os.path.exists(LOGO_PATH):
    logo = (
        ImageClip(LOGO_PATH)
        .set_duration(final_duration)
        .resize(width=80)
        .set_position(("right", "top"))
        .margin(right=15, top=15, opacity=0)
    )

# === Progress bar ===
def bar_frame(t):
    width = max(1, int(720 * t / final_duration))
    bar = np.zeros((5, 720, 3), dtype=np.uint8)
    bar[:, :width] = [255, 255, 255]
    return bar

bar = VideoClip(make_frame=bar_frame, duration=final_duration).set_position(("center", 0))

# === Compose all layers ===
layers = [bg, glass, bar] + texts
if logo: layers.append(logo)

final = CompositeVideoClip(layers, size=(720, 1280)).set_audio(final_audio).set_duration(final_duration)
final.write_videofile(OUTPUT_PATH, fps=24, codec="libx264", audio_codec="aac")

print(f"✅ Final reel exported to: {OUTPUT_PATH}")
