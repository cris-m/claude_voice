import inspect
import sys
from .base import BaseTTS


class MlxTTS(BaseTTS):

    def __init__(self, model_id, voice, language, instruct, streaming_interval=1.0):
        if sys.platform != "darwin":
            raise ImportError("mlx-audio requires macOS with Apple Silicon.")
        self.model_id = model_id
        self.voice = voice
        self.language = language
        self.instruct = instruct
        self.streaming_interval = streaming_interval
        self._model = None

    def _init_model(self):
        if self._model is not None:
            return
        from mlx_audio.tts.utils import load_model
        self._model = load_model(self.model_id)

    def _generate(self, text, kwargs, stream=False):
        extra = {}
        if stream:
            extra = {"stream": True, "streaming_interval": self.streaming_interval}
        return self._model.generate(
            text=text,
            voice=kwargs.get("voice", self.voice),
            instruct=kwargs.get("instruct", self.instruct),
            lang_code=kwargs.get("language", self.language),
            verbose=False,
            **extra,
        )

    def speak(self, text: str, **kwargs) -> None:
        import numpy as np

        self._init_model()

        chunks = []
        sample_rate = 24000
        for result in self._generate(text, kwargs):
            chunks.append(np.array(result.audio).flatten())
            sample_rate = result.sample_rate

        if not chunks:
            return

        self._play_audio(np.concatenate(chunks).astype(np.float32), sample_rate)

    @property
    def supports_streaming(self) -> bool:
        # Not every mlx-audio model implements streaming; check the signature.
        self._init_model()
        try:
            params = inspect.signature(self._model.generate).parameters
        except (TypeError, ValueError):
            return False
        return "stream" in params

    def speak_stream(self, text: str, **kwargs) -> None:
        import numpy as np

        self._init_model()
        self._play_stream(
            (np.array(r.audio).flatten(), r.sample_rate)
            for r in self._generate(text, kwargs, stream=True)
        )
