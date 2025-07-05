# generate_voiceover.py 🗣️
import os
import nltk
import json
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path

# Coqui XTTS TOS agreement
os.environ["COQUI_TOS_AGREED"] = "1"

# 📁 File paths
SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
MERGED_VOICEOVER = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO_PATH = "assets/ref.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

nltk.download("punkt", quiet=True)

def smart_chunking(script, max_chars=180):
    """Split script into natural, speakable chunks (not just short sentences)."""
    raw_sentences = nltk.sent_tokenize(script.strip())
    chunks, current = [], ""

    for sentence in raw_sentences:
        if len(current) + len(sentence) < max_chars:
            current += " " + sentence if current else sentence
        else:
            chunks.append(current.strip())
            current = sentence
    if current:
        chunks.append(current.strip())

    print(f"✂️ Script split into {len(chunks)} smart chunks.")
    return chunks

def generate_voiceover_chunks(chunks, output_dir):
    """Generate and store voiceover chunks with timestamps."""
    os.makedirs(output_dir, exist_ok=True)
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    for idx, sentence in enumerate(chunks):
        print(f"🎙️ Chunk {idx+1}/{len(chunks)}: {sentence}")
        filename = f"chunk_{idx+1:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        tts.tts_to_file(
            text=sentence,
            file_path=filepath,
            speaker_wav=REF_AUDIO_PATH,
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
    """Merge all MP3 chunks into a single voiceover."""
    combined = AudioSegment.empty()
    for file in sorted(Path(chunks_dir).glob("chunk_*.mp3")):
        combined += AudioSegment.from_file(file)
    combined.export(output_path, format="mp3")
    print(f"✅ Merged voiceover saved to: {output_path}")

def save_metadata(metadata, path):
    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved to: {path}")

def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    chunks = smart_chunking(script)
    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)
    merge_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_metadata(metadata, METADATA_FILE)

if __name__ == "__main__":
    main()
