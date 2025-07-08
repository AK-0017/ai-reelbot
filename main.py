import os
import shutil
from datetime import datetime
from auto_fetch_news import fetch_news_from_all_sources, generate_script, save_scripts
from auto_generate_script import extract_single_story, save_single_story
from supabase_uploader import upload_file_to_supabase

# === Step 1: Create temp session folder (not stored in Replit)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
session_dir = os.path.join("/tmp", timestamp)
os.makedirs(session_dir, exist_ok=True)
print(f"📁 Session folder created: {session_dir}")

# === Step 2: Fetch News from All Sources ===
news = fetch_news_from_all_sources()
if news:
    scripts = generate_script(news)
    save_scripts(scripts, session_dir)
else:
    print("❌ No news fetched. Skipping script generation.")

# === Step 3: Extract & Rewrite One Strong Script ===
script_path = os.path.join(session_dir, "script.txt")
final_story = extract_single_story(script_path)
if final_story:
    save_single_story(session_dir, final_story)
else:
    print("❌ No strong story extracted. Skipping upload.")

# === Step 4: Upload to Supabase and Clean ===
supabase_folder = f"scripts/{timestamp}"
try:
    upload_file_to_supabase(script_path, f"{supabase_folder}/script.txt")
    upload_file_to_supabase(os.path.join(session_dir, "single_script.txt"), f"{supabase_folder}/single_script.txt")
    print("✅ Uploaded both script files to Supabase.")
except Exception as e:
    print("❌ Supabase upload failed:", e)

# Optional: Cleanup temp folder (optional, since Replit /tmp is auto-wiped)
shutil.rmtree(session_dir)

print(f"\n✅ All done. Cleaned temp folder: {session_dir}")
