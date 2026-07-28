import json
import os
import platform

def get_data_path():
    app_name = "Personal Dashboard"
    
    if platform.system() == "Windows":
        base_dir = os.getenv("APPDATA")
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux
        base_dir = os.path.expanduser("~/.config")
        
    app_dir = os.path.join(base_dir, app_name)
    
    # Buat folder jika belum ada
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
        
    return os.path.join(app_dir, "data.json")

DATA_FILE = get_data_path()

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_data(data: dict):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Gagal menyimpan data: {e}")