import asyncio
import queue
import threading

from .base import BaseTTS
from .utils import download_kokoro_models

_DONE = object()


class KokoroTTS(BaseTTS):

    def __init__(self, voice="af_sarah"):
        self.voice = voice
        self._kokoro = None

    def _init_kokoro(self):
        if self._kokoro is not None:
            return
        from kokoro_onnx import Kokoro
        model_path, voices_path = download_kokoro_models()
        self._kokoro = Kokoro(model_path, voices_path)

    def _args(self, kwargs):
        return (
            kwargs.get("voice", self.voice),
            kwargs.get("speed", 1.0),
            kwargs.get("lang", "en-us"),
        )

    def speak(self, text: str, **kwargs) -> None:
        self._init_kokoro()
        voice, speed, lang = self._args(kwargs)
        samples, sample_rate = self._kokoro.create(text, voice=voice, speed=speed, lang=lang)
        self._play_audio(samples, sample_rate)

    @property
    def supports_streaming(self) -> bool:
        try:
            from kokoro_onnx import Kokoro
        except ImportError:
            return False
        return hasattr(Kokoro, "create_stream")

    def speak_stream(self, text: str, **kwargs) -> None:
        self._init_kokoro()
        voice, speed, lang = self._args(kwargs)
        q: queue.Queue = queue.Queue()

        # kokoro-onnx streams via an async generator; run it on a background
        # thread so playback (blocking writes) never stalls generation.
        async def produce():
            async for chunk in self._kokoro.create_stream(text, voice=voice, speed=speed, lang=lang):
                q.put(chunk)

        def run():
            try:
                asyncio.run(produce())
            except Exception as e:  # surface errors to the consumer
                q.put(e)
            finally:
                q.put(_DONE)

        threading.Thread(target=run, daemon=True).start()

        def chunks():
            while True:
                item = q.get()
                if item is _DONE:
                    return
                if isinstance(item, Exception):
                    raise item
                yield item

        self._play_stream(chunks())
