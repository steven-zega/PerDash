import json
import os
import platform

def get_data_path():
    app_name = "Personal Dashboard"
    
    # Deteksi lingkungan Android / Serious Python
    if "SERIOUS_PYTHON_APP_DATA_DIR" in os.environ:
        base_dir = os.environ["SERIOUS_PYTHON_APP_DATA_DIR"]
    elif "ANDROID_PRIVATE" in os.environ:
        base_dir = os.environ["ANDROID_PRIVATE"]
    elif "PYTHONHOME" in os.environ and "/tmp/serious_python" in os.environ.get("PYTHONHOME", ""):
        # Fallback direktori privat internal Android
        base_dir = os.path.dirname(os.environ.get("PYTHONHOME"))
    elif platform.system() == "Windows":
        base_dir = os.getenv("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux
        base_dir = os.path.expanduser("~/.config")
        
    app_dir = os.path.join(base_dir, app_name)
    
    if not os.path.exists(app_dir):
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