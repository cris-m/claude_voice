from .base import BaseTTS
from .utils import download_kokoro_models


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

    def speak(self, text: str, **kwargs) -> None:
        self._init_kokoro()
        voice = kwargs.get("voice", self.voice)
        speed = kwargs.get("speed", 1.0)
        lang = kwargs.get("lang", "en-us")
        samples, sample_rate = self._kokoro.create(text, voice=voice, speed=speed, lang=lang)
        self._play_audio(samples, sample_rate)
