# generate_voiceover.py 🎤 - Premium Voiceover Generator
import os
import json
import nltk
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path

# ✅ Automatically agree to Coqui TTS License
os.environ["COQUI_TOS_AGREED"] = "1"

# === Constants ===
SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
MERGED_VOICEOVER = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO_PATH = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

# Ensure punkt tokenizer is downloaded
nltk.download("punkt", quiet=True)

def split_script(script):
    """Smartly split the script into clean sentence chunks."""
    raw = nltk.sent_tokenize(script.strip())
    chunks = [s.strip().replace("\n", " ") for s in raw if s.strip()]
    print(f"✂️ Script split into {len(chunks)} chunks.")
    return chunks

def generate_voiceover_chunks(chunks, output_dir):
    """Generate TTS for each chunk and save metadata."""
    os.makedirs(output_dir, exist_ok=True)
    print("🎙️ Loading Coqui XTTS model...")
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    for idx, sentence in enumerate(chunks):
        if not sentence:
            continue

        print(f"🎤 Generating chunk {idx + 1}/{len(chunks)}: {sentence}")
        filename = f"chunk_{idx+1:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        # Generate the chunk using reference audio
        tts.tts_to_file(
            text=sentence,
            speaker_wav=REF_AUDIO_PATH,
            file_path=filepath,
            language=LANGUAGE
        )

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
    """Merge all generated audio chunks into one final voiceover file."""
    combined = AudioSegment.empty()
    for chunk_file in sorted(Path(chunks_dir).glob("chunk_*.mp3")):
        combined += AudioSegment.from_file(chunk_file)
    combined.export(output_path, format="mp3")
    print(f"✅ Final voiceover saved at: {output_path}")

def save_metadata(metadata, path):
    """Save voiceover chunk timing metadata as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved to: {path}")

def main():
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError(f"❌ Script not found: {SCRIPT_FILE}")
    if not os.path.exists(REF_AUDIO_PATH):
        raise FileNotFoundError(f"❌ Reference audio missing: {REF_AUDIO_PATH}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    chunks = split_script(script)
    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)
    merge_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_metadata(metadata, METADATA_FILE)

if __name__ == "__main__":
    main()
