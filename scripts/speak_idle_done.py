#!/usr/bin/env python3

import sys
import os
import json
import time

ACTIVITY_FILE = "/tmp/claude_voice_last_activity"
SUMMARY_SPOKEN_FILE = "/tmp/claude_voice_summary_spoken"
IDLE_THRESHOLD = 60  # seconds

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    stop_time = time.time()

    with open(ACTIVITY_FILE, "w") as f:
        f.write(str(stop_time))

    try:
        os.remove(SUMMARY_SPOKEN_FILE)
    except OSError:
        pass

    time.sleep(IDLE_THRESHOLD)

    try:
        with open(ACTIVITY_FILE, "r") as f:
            last_activity = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return

    if last_activity != stop_time:
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
