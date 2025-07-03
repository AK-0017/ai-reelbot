import os
from supabase import create_client
from datetime import datetime

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
BUCKET_NAME = "scripts"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_latest_folder():
    print(f"📦 Listing folders from bucket: {BUCKET_NAME}")
    response = supabase.storage.from_(BUCKET_NAME).list("", {"limit": 100})

    if not isinstance(response, list):
        raise Exception(f"❌ Unexpected Supabase response: {response}")

    folders = [obj["name"] for obj in response if obj.get("name") and obj["name"][0].isdigit()]
    folders.sort(reverse=True)
    if not folders:
        raise Exception("❌ No timestamped folders found in bucket.")
    return folders[0]

def download_latest_script():
    folder = get_latest_folder()
    print(f"📁 Latest folder: {folder}")
    local_path = f"temp/single_script.txt"
    remote_path = f"{folder}/single_script.txt"

    with open(local_path, "wb") as f:
        data = supabase.storage.from_(BUCKET_NAME).download(remote_path)
        f.write(data)
    print(f"✅ Script downloaded to: {local_path}")

if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    download_latest_script()
