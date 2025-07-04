# session.py ✅
import os
from datetime import datetime

def get_current_session_folder():
    """
    Returns the session folder name (timestamped) that was used to fetch the script.
    Falls back to generating a new one if none is found.
    """
    session_file = "temp/session_folder.txt"

    # ✅ Primary: Use the folder saved during script fetch
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            return f.read().strip()

    # 🛑 Fallback: Try detecting an existing folder in temp/
    temp_path = "temp"
    for name in os.listdir(temp_path):
        full_path = os.path.join(temp_path, name)
        if os.path.isdir(full_path) and name.count("-") == 2 and "_" in name:
            return name

    # 🕓 Final fallback: Generate a new timestamped name
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
