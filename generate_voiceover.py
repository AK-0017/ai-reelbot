# generate_voiceover.py 🎙️ Sentence-Based Voiceover Edition
import os
import nltk
import json
from TTS.api import TTS
from pydub import AudioSegment
from pathlib import Path

# ✅ Auto-agree to Coqui XTTS TOS
os.environ["COQUI_TOS_AGREED"] = "1"

# === File Paths ===
SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
MERGED_VOICEOVER = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
REF_AUDIO_PATH = "assets/ref.wav"

# === TTS Settings ===
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

# 📥 Ensure NLTK sentence tokenizer is available
nltk.download("punkt", quiet=True)


def split_into_sentences(text):
    """Split text into full natural sentences."""
    return nltk.sent_tokenize(text.strip())


def generate_voiceover(sentences, output_dir):
    """Generate voiceover chunks using XTTS for each full sentence."""
    os.makedirs(output_dir, exist_ok=True)
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

    metadata = []
    current_time = 0.0

    print("🗣️ Generating sentence-based voiceover...")

    for idx, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue

        filename = f"chunk_{idx+1:02d}.mp3"
        filepath = os.path.join(output_dir, filename)

        print(f"🎤 [{idx+1}/{len(sentences)}] {sentence}")

        # Generate TTS audio
        tts.tts_to_file(
            text=sentence,
            file_path=filepath,
            speaker_wav=REF_AUDIO_PATH,
            language=LANGUAGE
        )

        # Calculate duration
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


def merge_audio_chunks(input_dir, output_path):
    """Merge all chunk MP3s into one final voiceover."""
    combined = AudioSegment.empty()
    for file in sorted(Path(input_dir).glob("chunk_*.mp3")):
        combined += AudioSegment.from_file(file)
    combined.export(output_path, format="mp3")
    print(f"✅ Final voiceover saved: {output_path}")


def save_metadata(metadata, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Voiceover metadata saved: {path}")


def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    sentences = split_into_sentences(script)
    metadata = generate_voiceover(sentences, OUTPUT_DIR)
    merge_audio_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_metadata(metadata, METADATA_FILE)


if __name__ == "__main__":
    main()
