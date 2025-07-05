# captions_generator.py 🎬
import json
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

CHUNKS_METADATA = "temp/chunks_metadata.json"
VOICEOVER_FILE = "temp/voiceover.mp3"
INPUT_VIDEO = "temp/background.mp4"
OUTPUT_VIDEO = "temp/final_reel.mp4"

# 🧠 Caption Style
FONT = "Arial-Bold"
FONT_SIZE = 40
COLOR = "white"
SHADOW_COLOR = "black"
DURATION_PADDING = 0.2

def load_chunks_metadata(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_caption_clips(metadata, video_size):
    clips = []
    for chunk in metadata:
        text = chunk["text"]
        start = chunk["start"]
        end = chunk["end"]
        duration = end - start + DURATION_PADDING

        txt_clip = (
            TextClip(text, fontsize=FONT_SIZE, font=FONT, color=COLOR, stroke_color=SHADOW_COLOR, stroke_width=2, size=(video_size[0] * 0.9, None), method="caption")
            .set_position(("center", "bottom"))
            .set_start(start)
            .set_duration(duration)
            .fadein(0.3)
            .fadeout(0.3)
        )
        clips.append(txt_clip)
    return clips

def render_video():
    print("🎥 Generating final reel with synced captions...")
    video = VideoFileClip(INPUT_VIDEO)
    audio = AudioFileClip(VOICEOVER_FILE)
    metadata = load_chunks_metadata(CHUNKS_METADATA)

    caption_clips = generate_caption_clips(metadata, video.size)
    final = CompositeVideoClip([video] + caption_clips)
    final = final.set_audio(audio).set_duration(audio.duration)

    final.write_videofile(OUTPUT_VIDEO, codec="libx264", audio_codec="aac")
    print(f"✅ Final reel exported to: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    render_video()
