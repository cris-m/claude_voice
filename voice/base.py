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


class _SlicePlayer:
    """Writes audio to an output stream in ~100ms slices.

    Small slices keep signal handling prompt (speak.py --stop) and give a place
    to honour speak.py --pause: between slices, if the pause flag is set, let
    the buffered audio drain, stop the device, and wait for --resume.
    """

    poll = 0.1

    def __init__(self, stream, sample_rate: int):
        self.stream = stream
        self.step = max(1, sample_rate // 10)

    def write(self, samples) -> None:
        frames = samples.reshape(-1, 1)
        for i in range(0, len(frames), self.step):
            self._wait_if_paused()
            self.stream.write(frames[i:i + self.step])

    def _wait_if_paused(self) -> None:
        from .speaker import is_paused

        if not is_paused():
            return
        import time

        self.stream.stop()  # finish the buffered slice, then go quiet
        while is_paused():
            time.sleep(self.poll)
        self.stream.start()


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

        stream = None
        lock = audio_lock()
        lock.acquire()
        interrupted = False
        try:
            stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype="float32")
            stream.start()
            _SlicePlayer(stream, sample_rate).write(samples)
        except BaseException:
            interrupted = True
            raise
        finally:
            if stream is not None:
                if interrupted:
                    stream.abort()  # interrupted (e.g. speak.py --stop): cut audio now
                else:
                    stream.stop()  # blocks until buffered audio has played
                stream.close()
            lock.release()

    # Seconds of audio to queue before playback starts. Generation runs ahead
    # of playback on a background thread; this cushion absorbs hiccups on
    # machines where generation is only slightly faster than real time.
    stream_prebuffer = 0.5

    def _play_stream(self, chunks: Iterable[Tuple[object, int]]) -> None:
        """Play (samples, sample_rate) chunks while they are still being generated.

        Generation runs on a background thread that fills a queue, so the model
        keeps working while audio plays. (Generating and writing on one thread
        starves the device at every chunk boundary, because a blocking write
        only returns once the chunk has nearly finished playing.)
        """
        import queue
        import threading

        import sounddevice as sd

        q: "queue.Queue" = queue.Queue()
        done = object()

        def produce():
            try:
                for samples, sample_rate in chunks:
                    samples = _to_float32(samples)
                    if len(samples):
                        q.put((samples, sample_rate))
            except BaseException as e:  # hand errors to the playing thread
                q.put(e)
            finally:
                q.put(done)

        threading.Thread(target=produce, daemon=True).start()

        def next_item():
            # Poll so a SIGTERM from `speak.py --stop` is handled promptly.
            while True:
                try:
                    item = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                if isinstance(item, BaseException):
                    raise item
                return item

        # Queue up the prebuffer before touching the device or the audio lock.
        pending, buffered, finished = [], 0.0, False
        while buffered < self.stream_prebuffer:
            item = next_item()
            if item is done:
                finished = True
                break
            pending.append(item)
            buffered += len(item[0]) / item[1]
        if not pending:
            return

        stream = None
        lock = audio_lock()
        lock.acquire()
        interrupted = False
        try:
            sample_rate = pending[0][1]
            stream = sd.OutputStream(samplerate=sample_rate, channels=1, dtype="float32")
            stream.start()
            # Slices keep --stop prompt and let --pause take effect mid-chunk.
            write = _SlicePlayer(stream, sample_rate).write

            for samples, _ in pending:
                write(samples)
            while not finished:
                item = next_item()
                if item is done:
                    break
                write(item[0])
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
            lock.release()
