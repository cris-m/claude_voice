import os
import tempfile
import time
from abc import ABC, abstractmethod

AUDIO_LOCK_FILE = os.path.join(tempfile.gettempdir(), "claude_voice_audio.lock")


def acquire_lock() -> str:
    lock_path = AUDIO_LOCK_FILE + ".lck"
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock_path
        except FileExistsError:
            time.sleep(0.05)


def release_lock(lock_path: str) -> None:
    try:
        os.unlink(lock_path)
    except OSError:
        pass


class BaseTTS(ABC):

    @abstractmethod
    def speak(self, text: str, **kwargs) -> None:
        pass

    def _play_audio(self, samples, sample_rate: int) -> None:
        import numpy as np
        import sounddevice as sd

        if hasattr(samples, 'numpy'):
            samples = samples.squeeze().numpy()
        if not isinstance(samples, np.ndarray):
            samples = np.array(samples, dtype=np.float32)
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32)
        if len(samples) == 0:
            return

        lock_path = acquire_lock()
        try:
            sd.play(samples, sample_rate)
            sd.wait()
        finally:
            release_lock(lock_path)
