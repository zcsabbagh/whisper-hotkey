"""Configuration management for whisper-dictation."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "whisper-dictation"
CONFIG_FILE = CONFIG_DIR / "config.json"

MODELS = {
    "tiny.en": {
        "label": "tiny.en (Recommended)",
        "description": "~75MB, fastest, good for clear English dictation",
    },
    "distil-large-v3": {
        "label": "distil-large-v3",
        "description": "~1.5GB, slower but more accurate, handles accents/noise better",
    },
}

DEFAULT_MODEL = "tiny.en"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")


def get_model_id() -> str:
    config = load_config()
    return config.get("model", DEFAULT_MODEL)


def set_model_id(model_id: str):
    config = load_config()
    config["model"] = model_id
    save_config(config)
