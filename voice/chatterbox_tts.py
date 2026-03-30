from .base import BaseTTS


class ChatterboxTTS(BaseTTS):

    def __init__(self, model_variant="original", exaggeration=0.5, cfg_weight=0.5,
                 temperature=0.8, audio_prompt_path=None):
        self.model_variant = model_variant
        self.exaggeration = exaggeration
        self.cfg_weight = cfg_weight
        self.temperature = temperature
        self.audio_prompt_path = audio_prompt_path
        self._model = None
        self._device = None

    def _get_device(self):
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _init_model(self):
        if self._model is not None:
            return

        self._device = self._get_device()
        variant = self.model_variant

        if variant == "turbo" and self._device == "mps":
            variant = "original"

        if variant == "turbo":
            from chatterbox.tts_turbo import ChatterboxTurboTTS
            self._model = ChatterboxTurboTTS.from_pretrained(device=self._device)
        else:
            from chatterbox.tts import ChatterboxTTS as CBModel
            self._model = CBModel.from_pretrained(device=self._device)
        self._active_variant = variant

    def speak(self, text: str, **kwargs) -> None:
        import torch

        self._init_model()

        exaggeration = kwargs.get("exaggeration", self.exaggeration)
        cfg_weight = kwargs.get("cfg_weight", self.cfg_weight)
        temperature = kwargs.get("temperature", self.temperature)
        audio_prompt_path = kwargs.get("audio_prompt_path", self.audio_prompt_path)

        audio_prompt = None
        if audio_prompt_path:
            import torchaudio
            audio_prompt, _ = torchaudio.load(audio_prompt_path)

        gen_kwargs = {"audio_prompt": audio_prompt, "temperature": temperature}
        if self._active_variant != "turbo":
            gen_kwargs["exaggeration"] = exaggeration
            gen_kwargs["cfg_weight"] = cfg_weight

        with torch.no_grad():
            wav = self._model.generate(text, **gen_kwargs)

        self._play_audio(wav.squeeze().cpu(), self._model.sr)
