import json
import os
import sys
import tempfile

from .utils import clean_for_speech, download_kokoro_models

__version__ = "0.2.0"
__all__ = [
    "speak", "clean_for_speech", "download_kokoro_models",
    "load_config", "get_tts", "TEMP_DIR", "venv_python",
]

TEMP_DIR = tempfile.gettempdir()

_LANG_MAP = {"fr": "fr-fr", "zh": "cmn", "pt": "pt-br"}


def venv_python() -> str:
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sys.platform == "win32":
        return os.path.join(plugin_root, ".venv", "Scripts", "python.exe")
    return os.path.join(plugin_root, ".venv", "bin", "python")


def load_config() -> dict:
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(plugin_root, "voice_config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    if "kokoro" in config:
        lang = config["kokoro"].get("lang", "en-us")
        config["kokoro"]["lang"] = _LANG_MAP.get(lang, lang)
    return config


def get_tts(config: dict):
    provider = config["provider"]

    if provider == "chatterbox":
        from .chatterbox_tts import ChatterboxTTS
        cb = config["chatterbox"]
        return ChatterboxTTS(
            model_variant=cb["model_variant"],
            exaggeration=cb["exaggeration"],
            cfg_weight=cb["cfg_weight"],
            temperature=cb["temperature"],
            audio_prompt_path=cb.get("audio_prompt_path"),
        )
    elif provider == "mlx":
        from .mlx_tts import MlxTTS
        mx = config["mlx"]
        return MlxTTS(
            model_id=mx["model"],
            voice=mx["voice"],
            language=mx["language"],
            instruct=mx["instruct"],
        )
    else:
        from .kokoro_tts import KokoroTTS
        return KokoroTTS(voice=config["kokoro"]["voice"])


def speak(text: str, **kwargs) -> None:
    config = load_config()
    provider = config["provider"]
    tts = get_tts(config)

    if provider == "kokoro":
        ko = config["kokoro"]
        speak_kwargs = {
            "voice": kwargs.get("voice", ko["voice"]),
            "speed": kwargs.get("speed", ko["speed"]),
            "lang": kwargs.get("lang", ko["lang"]),
        }
    elif provider == "mlx":
        mx = config["mlx"]
        speak_kwargs = {
            "voice": kwargs.get("voice", mx["voice"]),
            "language": kwargs.get("language", mx["language"]),
            "instruct": kwargs.get("instruct", mx["instruct"]),
        }
    else:
        cb = config["chatterbox"]
        speak_kwargs = {
            "exaggeration": kwargs.get("exaggeration", cb["exaggeration"]),
            "cfg_weight": kwargs.get("cfg_weight", cb["cfg_weight"]),
            "temperature": kwargs.get("temperature", cb["temperature"]),
            "audio_prompt_path": kwargs.get("audio_prompt_path", cb.get("audio_prompt_path")),
        }

    tts.speak(text, **speak_kwargs)
