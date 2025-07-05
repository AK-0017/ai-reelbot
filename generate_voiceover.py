# generate_voiceover.py ✅ XTTS v2 with reference voice and chunking
import os
import json
import time
import nltk
from TTS.api import TTS

nltk.download("punkt")

INPUT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
METADATA_FILE = "temp/voiceover_metadata.json"
REFERENCE_VOICE = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

def load_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def chunk_text(text):
    from nltk.tokenize import sent_tokenize
    return sent_tokenize(text)

def generate_voiceover_chunks(chunks, output_dir):
    print("🗣️ Generating voiceover with Coqui XTTS v2...")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(REFERENCE_VOICE):
        raise FileNotFoundError(f"❌ Reference voice not found: {REFERENCE_VOICE}")

    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    total_time = 0.0

    for i, sentence in enumerate(chunks):
        filename = f"chunk_{i+1:02}.wav"
        filepath = os.path.join(output_dir, filename)

        print(f"🎙️ Generating chunk {i+1}/{len(chunks)}: {sentence}")
        start = time.time()
        tts.tts_to_file(
            text=sentence,
            file_path=filepath,
            speaker_wav=REFERENCE_VOICE,
            language=LANGUAGE
        )
        duration = time.time() - start
        metadata.append({
            "text": sentence,
            "file": filename,
            "start_time": round(total_time, 2),
            "end_time": round(total_time + duration, 2),
            "duration": round(duration, 2)
        })
        total_time += duration

    return metadata

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)

    script = load_script(INPUT_FILE)
    chunks = chunk_text(script)
    print(f"✂️ Script split into {len(chunks)} chunks.")

    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Voiceover chunks and metadata saved to: {OUTPUT_DIR}/ and {METADATA_FILE}")
