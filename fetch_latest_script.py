import os
from supabase import create_client
from datetime import datetime

# Supabase credentials from GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "scripts"
ROOT_FOLDER = "scripts"  # 👈 this is the nested folder inside the bucket

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📦 Step 1: Get latest timestamped folder inside 'scripts/'
def get_latest_folder():
    print(f"📦 Listing folders from bucket: {BUCKET_NAME}/{ROOT_FOLDER}")
    res = supabase.storage.from_(BUCKET_NAME).list(ROOT_FOLDER, {"limit": 100})
    data = res if isinstance(res, list) else res.get("data", [])
    folders = [obj["name"] for obj in data if obj["name"].strip("/")[-1].isdigit()]
    
    if not folders:
        raise Exception("❌ No timestamped folders found in bucket.")

    # Sort folders by timestamp string
    folders.sort(reverse=True)
    print(f"🕓 Latest folder: {folders[0]}")
    return folders[0].strip("/")


# 📥 Step 2: Download single_script.txt from that folder
def download_latest_script():
    folder = get_latest_folder()
    file_path = f"{ROOT_FOLDER}/{folder}/single_script.txt"
    print(f"⬇️ Downloading: {file_path}")
    
    res = supabase.storage.from_(BUCKET_NAME).download(file_path)
    if not res:
        raise Exception("❌ Failed to download single_script.txt")

    with open("temp/single_script.txt", "wb") as f:
        f.write(res)

    print("✅ Script downloaded to: temp/single_script.txt")
    
    # Inside download_latest_script()
    with open("temp/session_folder.txt", "w") as f:
    f.write(folder)



if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    download_latest_script()
