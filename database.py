import json
import os
import platform
import tempfile

def get_data_path():
    app_name = "Personal Dashboard"
    
    if platform.system() == "Windows":
        base_dir = os.getenv("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":
        base_dir = os.path.expanduser("~/Library/Application Support")
    elif "ANDROID_ARGUMENT" in os.environ or "PYTHONHOME" in os.environ or "ANDROID_PRIVATE" in os.environ:
        base_dir = os.environ.get("ANDROID_PRIVATE", tempfile.gettempdir())
    else:
        try:
            base_dir = os.path.expanduser("~/.config")
            test_dir = os.path.join(base_dir, app_name)
            os.makedirs(test_dir, exist_ok=True)
            return os.path.join(test_dir, "data.json")
        except PermissionError:
            base_dir = tempfile.gettempdir()

    app_dir = os.path.join(base_dir, app_name)
    os.makedirs(app_dir, exist_ok=True)
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