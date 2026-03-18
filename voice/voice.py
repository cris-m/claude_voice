import os
import tempfile
import time
from typing import Optional

import numpy as np
import sounddevice as sd

AUDIO_LOCK_FILE = os.path.join(tempfile.gettempdir(), "claude_voice_audio.lock")

from .utils import download_kokoro_models


def _acquire_lock() -> str:
    lock_path = AUDIO_LOCK_FILE + ".lck"
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock_path
        except FileExistsError:
            time.sleep(0.05)


def _release_lock(lock_path: str) -> None:
    """Release the lock by removing the lock file."""
    try:
        os.unlink(lock_path)
    except OSError:
        pass


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
            lock_path = _acquire_lock()
            try:
                sd.play(samples, sample_rate)
                sd.wait()
            finally:
                _release_lock(lock_path)


def speak(text: str, voice: str = "af_sarah", speed: float = 1.0, lang: str = "en-us") -> None:
    tts = KokoroTTS(voice=voice)
    tts.speak(text, voice=voice, speed=speed, lang=lang)
