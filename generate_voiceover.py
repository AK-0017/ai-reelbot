# generate_voiceover.py ✅ XTTS v2 (multi-speaker, no prompt)
import os
os.environ["COQUI_TOS_AGREED"] = "1"  # Skip ToS prompt

from TTS.api import TTS

INPUT_FILE = "temp/single_script.txt"
OUTPUT_FILE = "temp/voiceover.mp3"

# You can also try: "daniel", "poppy", "thorsten", "mai"
DEFAULT_SPEAKER = "poppy"
LANGUAGE = "en"

def load_script(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Script file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def synthesize(text, output_path):
    print("🗣️ Generating voiceover with Coqui XTTS v2...")
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=False)
    tts.tts_to_file(text=text, speaker=DEFAULT_SPEAKER, language=LANGUAGE, file_path=output_path)
    print(f"✅ Voiceover saved to: {output_path}")

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    script = load_script(INPUT_FILE)
    synthesize(script, OUTPUT_FILE)
