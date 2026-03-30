import sys
from .base import BaseTTS


class MlxTTS(BaseTTS):

    def __init__(self, model_id, voice, language, instruct):
        if sys.platform != "darwin":
            raise ImportError("mlx-audio requires macOS with Apple Silicon.")
        self.model_id = model_id
        self.voice = voice
        self.language = language
        self.instruct = instruct
        self._model = None

    def _init_model(self):
        if self._model is not None:
            return
        from mlx_audio.tts.utils import load_model
        self._model = load_model(self.model_id)

    def speak(self, text: str, **kwargs) -> None:
        import numpy as np

        self._init_model()

        voice = kwargs.get("voice", self.voice)
        instruct = kwargs.get("instruct", self.instruct)
        language = kwargs.get("language", self.language)

        chunks = []
        sample_rate = 24000
        for result in self._model.generate(
            text=text,
            voice=voice,
            instruct=instruct,
            lang_code=language,
            verbose=False,
        ):
            chunks.append(np.array(result.audio).flatten())
            sample_rate = result.sample_rate

        if not chunks:
            return

        self._play_audio(np.concatenate(chunks).astype(np.float32), sample_rate)
