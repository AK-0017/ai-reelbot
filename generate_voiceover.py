# generate_voiceover.py 🎙️
import os
import nltk
import json
from TTS.api import TTS
from pydub import AudioSegment
from datetime import datetime
from pathlib import Path

# ✅ Auto-agree to Coqui XTTS TOS
os.environ["COQUI_TOS_AGREED"] = "1"

# === Constants ===
SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
MERGED_VOICEOVER = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO_PATH = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

# 📥 Ensure sentence tokenizer is ready
nltk.download("punkt", quiet=True)

def split_script(script):
    """Split script into clean sentence chunks for TTS."""
    raw_sentences = nltk.sent_tokenize(script.strip())
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    print(f"✂️ Script split into {len(sentences)} smart chunks.")
    return sentences

def generate_voiceover_chunks(chunks, output_dir):
    """Generate TTS for each chunk and return metadata."""
    os.makedirs(output_dir, exist_ok=True)

    print("🗣️ Generating voiceover with Coqui XTTS v2...")
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    for idx, sentence in enumerate(chunks):
        sentence = sentence.strip()
        if not sentence:
            continue

        print(f"🎙️ Chunk {idx+1}/{len(chunks)}: {sentence}")
        filename = f"chunk_{idx+1:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        # Generate using reference voice
        tts.tts_to_file(
            text=sentence,
            file_path=filepath,
            speaker_wav=REF_AUDIO_PATH,
            language=LANGUAGE
        )

        # Get duration
        audio = AudioSegment.from_file(filepath)
        duration = len(audio) / 1000.0

        metadata.append({
            "text": sentence,
            "file": filename,
            "start": round(current_time, 2),
            "end": round(current_time + duration, 2),
            "duration": round(duration, 2)
        })

        current_time += duration

    return metadata

def merge_chunks(chunks_dir, output_path):
    """Merge all audio chunks into a single file."""
    combined = AudioSegment.empty()
    files = sorted(Path(chunks_dir).glob("chunk_*.mp3"))

    for file in files:
        segment = AudioSegment.from_file(file)
        combined += segment

    combined.export(output_path, format="mp3")
    print(f"✅ Final voiceover saved to: {output_path}")

def save_metadata(metadata, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Voiceover metadata saved to: {path}")

def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    chunks = split_script(script)
    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)
    merge_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_metadata(metadata, METADATA_FILE)

if __name__ == "__main__":
    main()
