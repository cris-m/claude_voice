#!/usr/bin/env python3

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import TEMP_DIR

ACTIVITY_FILE = os.path.join(TEMP_DIR, "claude_voice_last_activity")
SUMMARY_SPOKEN_FILE = os.path.join(TEMP_DIR, "claude_voice_summary_spoken")
IDLE_THRESHOLD = 60  # seconds


def main():
    stop_time = time.time()

    # Read current activity baseline — do NOT write, to avoid overwriting
    # a timestamp that record_command_start.py may have just set
    try:
        with open(ACTIVITY_FILE, "r") as f:
            baseline = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        baseline = stop_time

    try:
        os.remove(SUMMARY_SPOKEN_FILE)
    except OSError:
        pass

    time.sleep(IDLE_THRESHOLD)

    # If anything wrote a newer timestamp during our sleep, stay quiet
    try:
        with open(ACTIVITY_FILE, "r") as f:
            last_activity = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return

    if last_activity != baseline:
        return

    if os.path.exists(SUMMARY_SPOKEN_FILE):
        return

    from voice import speak, load_config

    config = load_config()
    speak(
        "Hey, I'm all done over here. Let me know if you need anything else.",
        voice=config["voice"],
        speed=config["speed"],
        lang=config["lang"],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
