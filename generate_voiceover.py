# generate_voiceover.py 🚀
import os
import json
import time
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path
import nltk

nltk.download("punkt")

# 🛠️ Config
INPUT_FILE = "temp/single_script.txt"
OUTPUT_FILE = "temp/voiceover.mp3"
CHUNKS_DIR = "temp/chunks"
METADATA_FILE = "temp/chunks_metadata.json"

MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"
SPEAKER = "coqui"  # Available default voice from model

# 📂 Ensure folders
os.makedirs("temp", exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)

def load_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def split_script(script, max_chars=220):
    """Chunk the script using sentence tokenization."""
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(script)
    
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) <= max_chars:
            current += " " + sent
        else:
            chunks.append(current.strip())
            current = sent
    if current:
        chunks.append(current.strip())
    return chunks

def synthesize_chunks(chunks, tts):
    metadata = []
    current_start = 0.0
    all_audio = AudioSegment.empty()

    for idx, text in enumerate(chunks):
        chunk_file = f"{CHUNKS_DIR}/chunk_{idx}.wav"
        print(f"🎤 Synthesizing chunk {idx+1}/{len(chunks)}...")

        tts.tts_to_file(
            text=text,
            speaker=SPEAKER,
            language=LANGUAGE,
            file_path=chunk_file
        )

        audio = AudioSegment.from_wav(chunk_file)
        duration = len(audio) / 1000.0  # sec

        metadata.append({
            "text": text,
            "start": round(current_start, 2),
            "end": round(current_start + duration, 2)
        })

        all_audio += audio
        current_start += duration

    all_audio.export(OUTPUT_FILE, format="mp3")
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Final voiceover saved to: {OUTPUT_FILE}")
    print(f"🧠 Metadata saved to: {METADATA_FILE}")

if __name__ == "__main__":
    print("🗣️ Generating voiceover with Coqui XTTS v2...")

    script = load_script(INPUT_FILE)
    chunks = split_script(script)
    print(f"✂️ Script split into {len(chunks)} chunks.")

    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)
    synthesize_chunks(chunks, tts)
