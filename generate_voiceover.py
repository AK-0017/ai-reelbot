import os
os.environ["COQUI_TOS_AGREED"] = "1"  # ✅ Bypass CPML agreement prompt

import nltk
import json
import datetime
from TTS.api import TTS
from pydub import AudioSegment

nltk.download("punkt")
from nltk.tokenize import sent_tokenize

SCRIPT_FILE = "temp/single_script.txt"
OUTPUT_DIR = "temp/voice_chunks"
VOICEOVER_FILE = "temp/voiceover.mp3"
METADATA_FILE = "temp/voiceover_metadata.json"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGUAGE = "en"
REFERENCE_WAV = "assets/ref.wav"

# ------------------------------
def read_script(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()

def split_into_chunks(script, max_chars=220):
    sentences = sent_tokenize(script)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    print(f"✂️ Script split into {len(chunks)} chunks.")
    return chunks

# ------------------------------
def generate_voiceover_chunks(chunks, output_dir):
    tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)
    os.makedirs(output_dir, exist_ok=True)

    metadata = []
    for i, sentence in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f"chunk_{i}.mp3")
        print(f"🎙️ Generating chunk {i+1}/{len(chunks)}: {sentence}")
        tts.tts_to_file(
            text=sentence,
            speaker_wav=REFERENCE_WAV,
            language=LANGUAGE,
            file_path=chunk_file
        )

        duration = AudioSegment.from_mp3(chunk_file).duration_seconds
        metadata.append({
            "text": sentence,
            "file": chunk_file,
            "start": None,  # to be filled later
            "duration": duration
        })

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Voiceover chunks and metadata saved to: {output_dir} and {METADATA_FILE}")
    return metadata

# ------------------------------
def combine_chunks_to_single_voiceover(chunks_folder, output_file):
    combined = AudioSegment.empty()
    chunk_files = sorted([
        os.path.join(chunks_folder, f) for f in os.listdir(chunks_folder)
        if f.endswith(".mp3")
    ])

    for f in chunk_files:
        combined += AudioSegment.from_mp3(f)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    combined.export(output_file, format="mp3")
    print(f"✅ Combined voiceover saved to: {output_file}")

# ------------------------------
if __name__ == "__main__":
    print("🗣️ Generating voiceover with Coqui XTTS v2...")
    script = read_script(SCRIPT_FILE)
    chunks = split_into_chunks(script)
    metadata = generate_voiceover_chunks(chunks, OUTPUT_DIR)
    combine_chunks_to_single_voiceover(OUTPUT_DIR, VOICEOVER_FILE)
