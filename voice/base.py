import os
import tempfile
import time
from abc import ABC, abstractmethod
from typing import Iterable, Tuple

AUDIO_LOCK_FILE = os.path.join(tempfile.gettempdir(), "claude_voice_audio.lock")


def _holder_alive(lock_path: str) -> bool:
    try:
        with open(lock_path) as f:
            pid = int(f.read().strip())
    except (OSError, ValueError):
        # Unreadable or empty: may be mid-write, so only treat it as stale if old.
        try:
            return time.time() - os.path.getmtime(lock_path) < 5
        except OSError:
            return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def acquire_lock() -> str:
    lock_path = AUDIO_LOCK_FILE + ".lck"
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock_path
        except FileExistsError:
            # A speaker killed mid-playback leaves its lock behind; reclaim it.
            if not _holder_alive(lock_path):
                release_lock(lock_path)
                continue
            time.sleep(0.05)


def release_lock(lock_path: str) -> None:
    try:
        os.unlink(lock_path)
    except OSError:
        pass


def _to_float32(samples):
    import numpy as np

    if hasattr(samples, 'numpy'):
        samples = samples.squeeze().numpy()
    if not isinstance(samples, np.ndarray):
        samples = np.array(samples, dtype=np.float32)
    if samples.dtype != np.float32:
        samples = samples.astype(np.float32)
    return samples.reshape(-1)


class BaseTTS(ABC):

    @abstractmethod
    def speak(self, text: str, **kwargs) -> None:
        pass

    @property
    def supports_streaming(self) -> bool:
        """Whether this provider can yield audio chunks while still generating."""
        return False

    def speak_stream(self, text: str, **kwargs) -> None:
        """Speak while generating. Falls back to speak() when unsupported."""
        self.speak(text, **kwargs)

    def _play_audio(self, samples, sample_rate: int) -> None:
        import sounddevice as sd

        samples = _to_float32(samples)
        if len(samples) == 0:
            return

        lock_path = acquire_lock()
        try:
            sd.play(samples, sample_rate)
            sd.wait()
        except BaseException:
            sd.stop()  # interrupted (e.g. speak.py --stop): cut audio now
            raise
        finally:
            release_lock(lock_path)

    def _play_stream(self, chunks: Iterable[Tuple[object, int]]) -> None:
        """Play (samples, sample_rate) chunks as they arrive.

        The output stream opens on the first non-empty chunk, so the audio lock
        is only held once there is something to play.
        """
        import sounddevice as sd

        stream = None
        lock_path = None
        interrupted = False
        try:
            for samples, sample_rate in chunks:
                samples = _to_float32(samples)
                if len(samples) == 0:
                    continue
                if stream is None:
                    lock_path = acquire_lock()
                    stream = sd.OutputStream(
                        samplerate=sample_rate, channels=1, dtype="float32"
                    )
                    stream.start()
                # Write in ~100ms slices: a blocking write of a long chunk would
                # delay signal handling (speak.py --stop) until it finished.
                step = max(1, sample_rate // 10)
                frames = samples.reshape(-1, 1)
                for i in range(0, len(frames), step):
                    stream.write(frames[i:i + step])
        except BaseException:
            interrupted = True
            raise
        finally:
            if stream is not None:
                if interrupted:
                    stream.abort()  # drop buffered audio immediately
                else:
                    stream.stop()  # blocks until buffered audio has played
                stream.close()
            if lock_path is not None:
                release_lock(lock_path)
