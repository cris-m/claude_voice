import json
import os

plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(plugin_root, "voice_config.json")

try:
    with open(config_path, "r") as f:
        config = json.load(f)
except Exception:
    config = {}

if not config.get("tts_summary_enabled", False):
    exit(0)

provider = config.get("provider", "kokoro")

instruction = """TTS Summary is enabled. End EVERY response with:
<!-- TTS_SUMMARY
Your spoken summary here (2-6 sentences, conversational, first person).
TTS_SUMMARY -->

Write as a natural spoken briefing. Avoid file paths, code, abbreviations, URLs, or special characters. Say "I fixed" not "The bug was fixed"."""

if provider == "chatterbox":
    instruction += """
Chatterbox renders emotion from text. Write with natural emotion — excitement, concern, satisfaction. Punctuation and emphasis affect delivery."""
elif provider == "mlx":
    instruction += """
MLX-Audio responds to both text emotion and the instruct field. Write naturally — the model adapts to conversational tone and emphasis."""

print(instruction)
