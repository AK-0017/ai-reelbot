import requests

SUPABASE_URL = "https://qtakfohimrxpupoodayr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF0YWtmb2hpbXJ4cHVwb29kYXlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjY5MTksImV4cCI6MjA2NzA0MjkxOX0.nyJv5PD1RpLgRsnazt3A76kjkTbgz5EyoNVH1UtcKxg"
BUCKET_NAME = "scripts"

def get_latest_folder():
    res = requests.get(
        f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}",
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        }
    )
    data = res.json()
    folders = [obj["name"] for obj in data if obj["name"] and obj["name"][0].isdigit()]
    folders.sort(reverse=True)
    return folders[0] if folders else None

def download_file(folder, filename, save_as):
    url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{folder}/{filename}"
    res = requests.get(url)
    if res.status_code == 200:
        with open(save_as, "wb") as f:
            f.write(res.content)
        print(f"✅ Downloaded: {save_as}")
    else:
        print(f"❌ Failed to download: {filename}")

if __name__ == "__main__":
    latest_folder = get_latest_folder()
    if latest_folder:
        print(f"📁 Latest folder: {latest_folder}")
        download_file(latest_folder, "single_script.txt", "single_script.txt")
    else:
        print("❌ No valid folders found.")
