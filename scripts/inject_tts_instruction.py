import json
import os
import sys

plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, plugin_root)

from voice.paths import read_config

try:
    config = read_config()
except Exception:
    config = {}

if not config.get("tts_summary_enabled", False):
    exit(0)

provider = config.get("provider", "kokoro")

from voice.lengths import LENGTHS, resolve_length

length = resolve_length(config.get("summary_length"))

instruction = f"""TTS Summary is enabled. End EVERY response with:
<!-- TTS_SUMMARY
Your spoken summary here (conversational, first person).
TTS_SUMMARY -->

Length ({length}): {LENGTHS[length]}

Write as a natural spoken briefing. Avoid file paths, code, abbreviations, URLs, or special characters. Say "I fixed" not "The bug was fixed"."""

if provider == "chatterbox":
    instruction += """
Chatterbox renders emotion from text. Write with natural emotion — excitement, concern, satisfaction. Punctuation and emphasis affect delivery."""
elif provider == "mlx":
    instruction += """
MLX-Audio responds to both text emotion and the instruct field. Write naturally — the model adapts to conversational tone and emphasis."""

print(instruction)
