# generate_voiceover.py 🎙️
import os
import nltk
import json
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path

# 📜 Auto-agree to license
os.environ["COQUI_TOS_AGREED"] = "1"

# === File Paths ===
SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
MERGED_VOICEOVER = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO_PATH = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

# Ensure sentence tokenizer is ready
nltk.download("punkt", quiet=True)

def split_script(script):
    """Break script into clean sentence chunks."""
    raw = nltk.sent_tokenize(script)
    return [line.strip() for line in raw if line.strip()]

def generate_voice_chunks(chunks, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    print("🎙️ Generating TTS chunks...")
    for i, sentence in enumerate(chunks):
        filename = f"chunk_{i+1:02d}.mp3"
        path = os.path.join(output_dir, filename)
        print(f"🔊 [{i+1}/{len(chunks)}] {sentence}")

        tts.tts_to_file(
            text=sentence,
            file_path=path,
            speaker_wav=REF_AUDIO_PATH,
            language=LANGUAGE
        )

        segment = AudioSegment.from_file(path)
        duration = len(segment) / 1000.0

        metadata.append({
            "text": sentence,
            "file": filename,
            "start": round(current_time, 2),
            "end": round(current_time + duration, 2),
            "duration": round(duration, 2)
        })

        current_time += duration

    return metadata

def merge_audio_chunks(chunks_dir, output_path):
    combined = AudioSegment.empty()
    files = sorted(Path(chunks_dir).glob("chunk_*.mp3"))

    for file in files:
        audio = AudioSegment.from_file(file)
        combined += audio

    combined.export(output_path, format="mp3")
    print(f"✅ Merged voiceover saved: {output_path}")

def save_metadata(metadata, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata written to: {path}")

def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    chunks = split_script(script)
    metadata = generate_voice_chunks(chunks, OUTPUT_DIR)
    merge_audio_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_metadata(metadata, METADATA_FILE)

if __name__ == "__main__":
    main()
