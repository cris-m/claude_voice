#!/usr/bin/env python3

import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import clean_for_speech, load_config
from voice.paths import state_dir
from voice.speaker import speak_detached

ERROR_LOG = os.path.join(state_dir(), "speak_summary_error.log")
DEBUG_LOG = os.path.join(state_dir(), "speak_summary_debug.log")

def extract_summary(text: str) -> str | None:
    pattern = r'<!--\s*TTS_SUMMARY\s*\n?(.*?)\n?TTS_SUMMARY\s*-->'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return clean_for_speech(match.group(1).strip())
    return None

def get_last_assistant_message_from_transcript(transcript_path: str) -> str | None:
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
                if entry.get("type") == "assistant":
                    message = entry.get("message", {})
                    content = message.get("content", [])
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif isinstance(block, str):
                            text_parts.append(block)
                    if text_parts:
                        return "\n".join(text_parts)
            except json.JSONDecodeError:
                continue
    except Exception as e:
        with open(ERROR_LOG, "a") as f:
            f.write(f"Error reading transcript: {e}\n")
    return None

def log_debug(msg):
    with open(DEBUG_LOG, "a") as f:
        f.write(f"{msg}\n")

def main():
    try:
        # Respect speak mode being switched off mid-session, even if Claude
        # still emits a summary block from earlier instructions.
        if not load_config().get("tts_summary_enabled", False):
            log_debug("Speak mode off; skipping")
            return

        input_data = sys.stdin.read().strip()
        if not input_data:
            log_debug("No input data")
            return

        data = json.loads(input_data)

        last_response = data.get("last_assistant_message")

        if not last_response:
            transcript_path = data.get("transcript_path")
            if not transcript_path or not os.path.exists(transcript_path):
                log_debug(f"No transcript: {transcript_path}")
                return
            last_response = get_last_assistant_message_from_transcript(transcript_path)
        if not last_response:
            log_debug("No last response found")
            return

        log_debug(f"Last response length: {len(last_response)}")

        summary = extract_summary(last_response)
        if summary:
            # Log only the size: summaries can quote private conversation content.
            log_debug(f"Speaking summary ({len(summary)} chars)")
            # Detached: long and podcast summaries outlast the hook timeout.
            speak_detached(summary, summary=True)
        else:
            log_debug("No TTS_SUMMARY found in response")

    except Exception as e:
        with open(ERROR_LOG, "a") as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    main()
