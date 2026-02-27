import os
import sys
from typing import Optional

import numpy as np
import sounddevice as sd

from .utils import download_kokoro_models

if sys.platform == "darwin":
    _brew_lib = "/opt/homebrew/lib"
    if os.path.isdir(_brew_lib):
        os.environ.setdefault("DYLD_LIBRARY_PATH", _brew_lib)


class KokoroTTS:
    DEFAULT_VOICE = "af_sarah"

    def __init__(self, voice: Optional[str] = None, sample_rate: int = 24000):
        self.voice = voice or self.DEFAULT_VOICE
        self.sample_rate = sample_rate
        self._kokoro = None

    def _init_kokoro(self) -> None:
        if self._kokoro is not None:
            return
        from kokoro_onnx import Kokoro
        model_path, voices_path = download_kokoro_models()
        self._kokoro = Kokoro(model_path, voices_path)

    def speak(self, text: str, voice: Optional[str] = None, speed: float = 1.0, lang: str = "en-us") -> None:
        self._init_kokoro()
        voice_id = voice or self.voice
        samples, sample_rate = self._kokoro.create(text, voice=voice_id, speed=speed, lang=lang)
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)
        if len(samples) > 0:
            sd.play(samples, sample_rate)
            sd.wait()


def speak(text: str, voice: str = "af_sarah", speed: float = 1.0, lang: str = "en-us") -> None:
    tts = KokoroTTS(voice=voice)
    tts.speak(text, voice=voice, speed=speed, lang=lang)
