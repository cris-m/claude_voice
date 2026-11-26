
from .paths import read_config, venv_python
from .utils import clean_for_speech, download_kokoro_models

__all__ = [
    "speak", "clean_for_speech", "download_kokoro_models",
    "load_config", "get_tts", "venv_python", "follow_up",
]

# Defaults for the spoken follow-ups that hooks fire without Claude's involvement.
FOLLOW_UP_DEFAULTS = {
    "command_done": {
        "enabled": True,
        "threshold_seconds": 30,
        "message": "Done! Ready when you are.",
    },
    "idle_done": {
        "enabled": True,
        "threshold_seconds": 60,
        "message": "Hey, I'm all done over here. Let me know if you need anything else.",
    },
    "notification": {
        "enabled": True,
    },
}

_LANG_MAP = {"fr": "fr-fr", "zh": "cmn", "pt": "pt-br"}


def load_config() -> dict:
    config = read_config()
    if "kokoro" in config:
        lang = config["kokoro"].get("lang", "en-us")
        config["kokoro"]["lang"] = _LANG_MAP.get(lang, lang)
    return config


def follow_up(config: dict, name: str) -> dict:
    """Resolved settings for one follow-up, with types coerced.

    `config` comes from load_config(), which already layers the user's file
    (including legacy `messages`) over the bundled defaults.
    """
    defaults = FOLLOW_UP_DEFAULTS.get(name, {})
    settings = dict(defaults)
    user = config.get("follow_ups", {}).get(name, {})
    if isinstance(user, dict):
        settings.update(user)
    settings["enabled"] = _as_bool(settings.get("enabled", True))
    if "threshold_seconds" in defaults:
        try:
            settings["threshold_seconds"] = float(settings["threshold_seconds"])
        except (TypeError, ValueError):
            settings["threshold_seconds"] = float(defaults["threshold_seconds"])
    if "message" in defaults and not isinstance(settings.get("message"), str):
        settings["message"] = defaults["message"]
    return settings


def _as_bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in ("false", "0", "no", "off", "")
    return bool(value)


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
            streaming_interval=mx.get("streaming_interval", 1.0),
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

    if config.get("streaming", True) and tts.supports_streaming:
        try:
            tts.stream_prebuffer = max(0.0, float(config.get("stream_prebuffer_seconds", 0.5)))
        except (TypeError, ValueError):
            pass
        tts.speak_stream(text, **speak_kwargs)
    else:
        tts.speak(text, **speak_kwargs)
