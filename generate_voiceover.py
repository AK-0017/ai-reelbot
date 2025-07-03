# generate_voiceover.py ✅
import os
from TTS.api import TTS

INPUT_FILE = "temp/single_script.txt"
OUTPUT_FILE = "temp/voiceover.mp3"

def load_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def synthesize(text, output_path):
    print("🗣️ Generating voiceover with Coqui TTS...")
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
    tts.tts_to_file(text=text, file_path=output_path)
    print(f"✅ Voiceover saved to: {output_path}")

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    script = load_script(INPUT_FILE)
    synthesize(script, OUTPUT_FILE)
