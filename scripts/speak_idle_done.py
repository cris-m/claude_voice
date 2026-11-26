#!/usr/bin/env python3

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import TEMP_DIR, load_config, follow_up

ACTIVITY_FILE = os.path.join(TEMP_DIR, "claude_voice_last_activity")
SUMMARY_SPOKEN_FILE = os.path.join(TEMP_DIR, "claude_voice_summary_spoken")
# The Stop hook running this script has a 180s timeout in hooks.json.
MAX_IDLE_THRESHOLD = 170


def main():
    stop_time = time.time()

    settings = follow_up(load_config(), "idle_done")
    if not settings["enabled"]:
        return
    threshold = min(float(settings["threshold_seconds"]), MAX_IDLE_THRESHOLD)

    try:
        with open(ACTIVITY_FILE, "r") as f:
            baseline = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        baseline = stop_time

    try:
        os.remove(SUMMARY_SPOKEN_FILE)
    except OSError:
        pass

    time.sleep(threshold)

    try:
        with open(ACTIVITY_FILE, "r") as f:
            last_activity = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return

    if last_activity != baseline:
        return

    if os.path.exists(SUMMARY_SPOKEN_FILE):
        return

    from voice import speak

    speak(settings["message"])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
