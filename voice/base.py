import os
from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from .paths import FileLock, state_dir


def audio_lock() -> FileLock:
    """Serialises playback so two speakers never talk over each other."""
    return FileLock(os.path.join(state_dir(), "audio.lock"))


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

        lock = audio_lock()
        lock.acquire()
        try:
            sd.play(samples, sample_rate)
            sd.wait()
        except BaseException:
            sd.stop()  # interrupted (e.g. speak.py --stop): cut audio now
            raise
        finally:
            lock.release()

    def _play_stream(self, chunks: Iterable[Tuple[object, int]]) -> None:
        """Play (samples, sample_rate) chunks as they arrive.

        The output stream opens on the first non-empty chunk, so the audio lock
        is only held once there is something to play.
        """
        import sounddevice as sd

        stream = None
        lock = None
        interrupted = False
        try:
            for samples, sample_rate in chunks:
                samples = _to_float32(samples)
                if len(samples) == 0:
                    continue
                if stream is None:
                    lock = audio_lock()
                    lock.acquire()
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
            if lock is not None:
                lock.release()
