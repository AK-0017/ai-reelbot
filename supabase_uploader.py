from supabase import create_client
import mimetypes
import os

# 🗝️ Replace with your actual URL and API key
SUPABASE_URL = "https://qtakfohimrxpupoodayr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF0YWtmb2hpbXJ4cHVwb29kYXlyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NjY5MTksImV4cCI6MjA2NzA0MjkxOX0.nyJv5PD1RpLgRsnazt3A76kjkTbgz5EyoNVH1UtcKxg"

# 🎯 Supabase bucket name
BUCKET_NAME = "scripts"

# 🔌 Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(local_path, remote_path):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    mime_type, _ = mimetypes.guess_type(local_path)
    with open(local_path, "rb") as f:
        data = f.read()

    # Perform upload (will overwrite if file exists)
    response = supabase.storage.from_(BUCKET_NAME).upload(
        remote_path,
        data,
        {"content-type": mime_type or "text/plain"},
    )

    # ✅ Check for success
    if not response:
        raise Exception("Upload failed with no response")
    if hasattr(response, 'status_code') and response.status_code >= 400:
        raise Exception(f"Upload failed: {response}")

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{remote_path}"
    print(f"📤 Uploaded to: {public_url}")
    return public_url
