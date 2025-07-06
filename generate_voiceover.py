# generate_voiceover.py 🎙️ + 📜 Caption Chunk Enhanced Edition

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
CAPTIONS_FILE = "temp/caption_chunks.json"
REF_AUDIO_PATH = "assets/ref.wav"

# === TTS Settings ===
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"

# 📥 Ensure NLTK sentence tokenizer is available
nltk.download("punkt", quiet=True)


def split_into_sentences(text):
    return nltk.sent_tokenize(text.strip())


def split_sentence_into_caption_chunks(sentence, max_words=6):
    """Split a sentence into smaller caption chunks of ~5-7 words."""
    words = sentence.strip().split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = words[i:i+max_words]
        if chunk:
            chunks.append(" ".join(chunk))
    return chunks


def generate_voiceover(sentences, output_dir):
    """Generate XTTS audio for sentence-wise chunks, return voiceover metadata."""
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

        # Generate TTS
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


def generate_caption_chunks(voiceover_metadata, max_words=6):
    """Break each sentence into caption chunks and distribute timings."""
    captions = []

    for item in voiceover_metadata:
        sentence = item["text"]
        start = item["start"]
        end = item["end"]
        duration = item["duration"]

        chunks = split_sentence_into_caption_chunks(sentence, max_words)
        num_chunks = len(chunks)
        if num_chunks == 0:
            continue

        chunk_duration = duration / num_chunks

        for i, chunk in enumerate(chunks):
            chunk_start = round(start + i * chunk_duration, 2)
            chunk_end = round(chunk_start + chunk_duration, 2)
            captions.append({
                "text": chunk,
                "start": chunk_start,
                "end": chunk_end,
                "duration": round(chunk_duration, 2)
            })

    return captions


def merge_audio_chunks(input_dir, output_path):
    combined = AudioSegment.empty()
    for file in sorted(Path(input_dir).glob("chunk_*.mp3")):
        combined += AudioSegment.from_file(file)
    combined.export(output_path, format="mp3")
    print(f"✅ Final voiceover saved: {output_path}")


def save_json(data, path, label="File"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ {label} saved: {path}")


def main():
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script = f.read()

    sentences = split_into_sentences(script)
    voiceover_meta = generate_voiceover(sentences, OUTPUT_DIR)
    captions_meta = generate_caption_chunks(voiceover_meta)

    merge_audio_chunks(OUTPUT_DIR, MERGED_VOICEOVER)
    save_json(voiceover_meta, METADATA_FILE, "Voiceover metadata")
    save_json(captions_meta, CAPTIONS_FILE, "Caption chunks")


if __name__ == "__main__":
    main()
