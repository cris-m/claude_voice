#!/usr/bin/env python3

import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import speak, clean_for_speech, load_config

def extract_summary(text: str) -> str | None:
    pattern = r'<!--\s*TTS_SUMMARY\s*\n?(.*?)\n?TTS_SUMMARY\s*-->'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return clean_for_speech(match.group(1).strip())
    return None

def get_last_assistant_message(transcript_path: str) -> str | None:
    try:
        with open(transcript_path, 'r') as f:
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
        with open("/tmp/speak_summary_error.log", "a") as f:
            f.write(f"Error reading transcript: {e}\n")
    return None

def log_debug(msg):
    with open("/tmp/speak_summary_debug.log", "a") as f:
        f.write(f"{msg}\n")

def main():
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            log_debug("No input data")
            return

        data = json.loads(input_data)
        transcript_path = data.get("transcript_path")
        if not transcript_path or not os.path.exists(transcript_path):
            log_debug(f"No transcript: {transcript_path}")
            return

        last_response = get_last_assistant_message(transcript_path)
        if not last_response:
            log_debug("No last response found")
            return

        log_debug(f"Last response length: {len(last_response)}")

        summary = extract_summary(last_response)
        if summary:
            log_debug(f"Speaking: {summary}")
            config = load_config()
            speak(summary, voice=config["voice"], speed=config["speed"], lang=config["lang"])
        else:
            log_debug("No TTS_SUMMARY found in response")

    except Exception as e:
        with open("/tmp/speak_summary_error.log", "a") as f:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    main()
