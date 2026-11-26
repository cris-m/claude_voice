#!/usr/bin/env python3
"""Stop hook: after a quiet period, let the user know Claude has finished.

Skipped if the user did anything in the meantime, or if a summary was already
spoken for this turn (always-on summary or the speak skill).
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import load_config, follow_up
from voice.paths import state_dir
from voice.speaker import last_summary_spoken, speak_detached

# The Stop hook running this script has a 600s timeout in hooks.json. Speech
# itself runs detached, so only the wait has to fit inside it.
MAX_IDLE_THRESHOLD = 580


def _read_time(name: str) -> float:
    try:
        with open(os.path.join(state_dir(), name)) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return 0.0


def main():
    settings = follow_up(load_config(), "idle_done")
    if not settings["enabled"]:
        return
    threshold = max(0.0, min(settings["threshold_seconds"], MAX_IDLE_THRESHOLD))

    baseline = _read_time("last_activity")
    time.sleep(threshold)

    if _read_time("last_activity") != baseline:
        return  # the user did something in the meantime
    if last_summary_spoken() >= _read_time("last_prompt"):
        return  # a summary was already spoken since the last message

    speak_detached(settings["message"])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
