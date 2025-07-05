# generate_voiceover.py ✅ XTTS v2 with Chunking Support
import os
import json
import nltk
from TTS.api import TTS
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment

# Auto-agree to Coqui license (required for CI/CD like GitHub Actions)
os.environ["COQUI_TOS_AGREED"] = "1"

INPUT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp"
CHUNK_PREFIX = "voice_chunk"
METADATA_FILE = os.path.join(OUTPUT_DIR, "voice_chunks_metadata.json")
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

def load_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def chunk_script(text):
    nltk.download("punkt")
    return sent_tokenize(text)

def generate_voiceover_chunks(chunks, output_dir):
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)
    metadata = []
    total_duration = 0.0

    for i, sentence in enumerate(chunks):
        filename = f"{CHUNK_PREFIX}_{i}.mp3"
        filepath = os.path.join(output_dir, filename)

        print(f"🎙️ Generating chunk {i+1}/{len(chunks)}: {sentence}")
        tts.tts_to_file(text=sentence, file_path=filepath, speaker_wav=None, language=LANGUAGE)

        audio = AudioSegment.from_file(filepath)
        duration_sec = len(audio) / 1000.0

        metadata.append({
            "chunk": i,
            "text": sentence,
            "file": filename,
            "start_time": round(total_duration, 2),
            "end_time": round(total_duration + duration_sec, 2)
        })

        total_duration += duration_sec

    return metadata

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    script = load_script(INPUT_FILE)
    chunks = chunk_script(script)
    print(f"✂️ Script split into {len(chunks)} chunks.")

    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Voice chunks and metadata saved to: {OUTPUT_DIR}")
