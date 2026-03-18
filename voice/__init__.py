import json
import os
import sys
import tempfile

from .voice import KokoroTTS, speak
from .utils import clean_for_speech, download_kokoro_models

__version__ = "0.1.0"
__all__ = [
    "KokoroTTS", "speak", "clean_for_speech", "download_kokoro_models",
    "load_config", "TEMP_DIR", "venv_python",
]

TEMP_DIR = tempfile.gettempdir()


def venv_python() -> str:
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sys.platform == "win32":
        return os.path.join(plugin_root, ".venv", "Scripts", "python.exe")
    return os.path.join(plugin_root, ".venv", "bin", "python")

_DEFAULTS = {
    "voice": "am_michael",
    "speed": 1.2,
    "lang": "en-us",
}

# Map user-friendly language codes to espeak-compatible codes.
_LANG_MAP = {
    "fr": "fr-fr",
    "zh": "cmn",
    "pt": "pt-br",
}

def load_config() -> dict:
    """Load voice settings from voice_config.json, falling back to defaults."""
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(plugin_root, "voice_config.json")
    try:
        with open(config_path, "r") as f:
            user_config = json.load(f)
        config = {**_DEFAULTS, **user_config}
    except Exception:
        config = dict(_DEFAULTS)
    # Normalize language code for espeak compatibility.
    config["lang"] = _LANG_MAP.get(config["lang"], config["lang"])
    return config
