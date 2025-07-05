# captions_generator.py 🎬
import os
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

# === File paths ===
CHUNKS_METADATA = "temp/voiceover_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# === Caption Style Settings ===
FONT = "Arial-Bold"
FONT_SIZE = 42
COLOR = "white"
SHADOW_COLOR = "black"
DURATION_PADDING = 0.2  # adds smoothness between captions

def load_chunks_metadata(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Metadata file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_caption_clips(metadata, video_size):
    clips = []
    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = max(0.5, end - start + DURATION_PADDING)

        caption = (
            TextClip(
                text,
                fontsize=FONT_SIZE,
                font=FONT,
                color=COLOR,
                stroke_color=SHADOW_COLOR,
                stroke_width=2,
                size=(int(video_size[0] * 0.9), None),
                method="caption",
            )
            .set_position(("center", "bottom"))
            .set_start(start)
            .set_duration(duration)
            .fadein(0.2)
            .fadeout(0.2)
        )
        clips.append(caption)
    return clips

def render_video():
    print("🎥 Generating final reel with synced captions...")

    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError(f"❌ Background video missing: {INPUT_VIDEO}")
    if not os.path.exists(VOICEOVER_FILE):
        raise FileNotFoundError(f"❌ Voiceover audio missing: {VOICEOVER_FILE}")

    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_chunks_metadata(CHUNKS_METADATA)

    captions = generate_caption_clips(metadata, video.size)
    final_clip = CompositeVideoClip([video] + captions)
    final_clip = final_clip.set_audio(audio).set_duration(audio.duration)

    final_clip.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac", fps=24)
    print(f"✅ Final reel exported to: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
