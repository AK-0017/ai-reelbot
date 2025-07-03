import os
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "scripts"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}


def get_latest_folder():
    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}?limit=100"
    res = requests.get(url, headers=HEADERS)
    try:
        data = res.json()
    except Exception as e:
        raise Exception(f"❌ JSON parsing failed: {e}\nRaw response:\n{res.text}")

    if not isinstance(data, list):
        raise Exception(f"❌ Unexpected Supabase response: {data}")

    # Extract folder names from file paths like '2025-07-02_20-12-05/script.txt'
    folders = set()
    for obj in data:
        name = obj.get("name", "")
        if "/" in name:
            folder = name.split("/")[0]
            if folder[0].isdigit():
                folders.add(folder)

    if not folders:
        raise Exception("❌ No valid timestamp folders found in Supabase.")

    latest_folder = sorted(folders, reverse=True)[0]
    return latest_folder


def download_script(folder):
    files = ["script.txt", "single_script.txt"]
    os.makedirs("temp", exist_ok=True)

    for filename in files:
        url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{folder}/{filename}"
        res = requests.get(url)
        if res.status_code == 200:
            with open(f"temp/{filename}", "wb") as f:
                f.write(res.content)
            print(f"✅ Downloaded: {filename}")
        else:
            raise Exception(f"❌ Failed to download {filename} | Status code: {res.status_code}")

if __name__ == "__main__":
    folder = get_latest_folder()
    print(f"📁 Latest folder detected: {folder}")
    download_script(folder)
