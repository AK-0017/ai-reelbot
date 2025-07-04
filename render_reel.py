# render_reel.py ✅
import os
import numpy as np
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    ColorClip, ImageClipm CompositeAudioClip
)
from moviepy.video.fx.all import crop

# === CONFIG ===
DURATION = 30
SCRIPT_PATH = "temp/single_script.txt"
VOICE_PATH = "temp/voiceover.mp3"
MUSIC_PATH = "temp/music.mp3"
BACKGROUND_PATH = "temp/background.mp4"
OUTPUT_PATH = "temp/final_reel.mp4"
LOGO_PATH = "assets/logo.png"

# === Load Script ===
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script = f.read().strip().split("\n")
    script = [line for line in script if line.strip()]

# === Load Audio ===
voice = AudioFileClip(VOICE_PATH)
music = AudioFileClip(MUSIC_PATH).volumex(0.2)  # lower bg music
audio = voice.set_start(0).audio_fadein(1).fx(lambda a: a.volumex(1.0)).audio_fadeout(1)
audio = audio.set_duration(DURATION)
final_audio = CompositeAudioClip([music.volumex(0.2), audio])

# === Background Video ===
bg = VideoFileClip(BACKGROUND_PATH).subclip(0, DURATION)
bg = crop(bg.resize(width=720), width=720, height=1280)
bg = bg.resize(lambda t: 1 + 0.02 * t)  # slow zoom

# === Glass Panel Overlay ===
glass = ColorClip((720, 460), (0, 0, 0)).set_opacity(0.4).set_duration(DURATION).set_position(("center", 400))

# === Text Animations ===
def anim_text(txt, y, start, size=48, dur=4):
    return (
        TextClip(txt, fontsize=size, color="white", font="Arial-Bold", method="caption", size=(660, None))
        .set_duration(dur).set_start(start)
        .set_position(("center", y))
        .crossfadein(0.5).crossfadeout(0.4)
    )

texts = []
y = 410
start = 1
for i, line in enumerate(script[:6]):
    texts.append(anim_text(line, y + i*60, start + i*2, size=52 if i == 0 else 48))

# === Follow CTA ===
cta = anim_text("📲 Follow for daily AI updates!", 1180, 26, size=42)
texts.append(cta)

# === Logo Watermark (Optional) ===
logo = None
if os.path.exists(LOGO_PATH):
    logo = (
        ImageClip(LOGO_PATH)
        .set_duration(DURATION)
        .resize(width=80)
        .set_position(("right", "top"))
        .margin(right=15, top=15, opacity=0)
    )

# === Progress Bar ===
def bar_frame(t):
    width = max(1, int(720 * t / DURATION))
    bar = np.zeros((5, 720, 3), dtype=np.uint8)
    bar[:, :width] = [255, 255, 255]
    return bar

from moviepy.video.VideoClip import VideoClip
bar = VideoClip(make_frame=bar_frame, duration=DURATION).set_position(("center", 0))

# === Compose Final Reel ===
layers = [bg, glass, bar] + texts
if logo: layers.append(logo)

final = CompositeVideoClip(layers, size=(720, 1280)).set_audio(final_audio).set_duration(DURATION)
final.write_videofile(OUTPUT_PATH, fps=24, codec="libx264", audio_codec="aac")

print(f"✅ Final reel exported to: {OUTPUT_PATH}")
