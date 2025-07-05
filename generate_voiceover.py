# generate_voiceover.py 🎙️ (Upgraded)
import os
import nltk
import json
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path

# === Auto-agree to XTTS license ===
os.environ["COQUI_TOS_AGREED"] = "1"

# === File paths ===
SCRIPT_FILE = "temp/single_script.txt"
CHUNKS_DIR = "temp/voice_chunks"
VOICEOVER_FILE = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

nltk.download("punkt", quiet=True)

def split_sentences(script):
    sentences = nltk.sent_tokenize(script.strip())
    return [s.strip() for s in sentences if s.strip()]

def generate_voice_chunks(sentences, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    for i, sentence in enumerate(sentences):
        filename = f"chunk_{i+1:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        print(f"🎤 Synthesizing chunk {i+1}/{len(sentences)}")
        tts.tts_to_file(
            text=sentence,
            speaker_wav=REF_AUDIO,
            language=LANGUAGE,
            file_path=filepath
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

def merge_chunks(input_dir, output_path):
    merged = AudioSegment.empty()
    for file in sorted(Path(input_dir).glob("chunk_*.mp3")):
        merged += AudioSegment.from_file(file)
    merged.export(output_path, format="mp3")
    print(f"✅ Voiceover exported: {output_path}")

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Metadata saved: {path}")

def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()
    sentences = split_sentences(script)
    metadata = generate_voice_chunks(sentences, CHUNKS_DIR)
    merge_chunks(CHUNKS_DIR, VOICEOVER_FILE)
    save_json(metadata, METADATA_FILE)

if __name__ == "__main__":
    main()
