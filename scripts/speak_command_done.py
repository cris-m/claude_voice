#!/usr/bin/env python3

import sys
import os
import time

STAMP_FILE = "/tmp/claude_voice_last_command"
DELAY = 15

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    my_time = time.time()
    with open(STAMP_FILE, "w") as f:
        f.write(str(my_time))

    time.sleep(DELAY)

    try:
        with open(STAMP_FILE, "r") as f:
            last_time = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return

    if last_time != my_time:
        return

    from voice import speak, load_config

    config = load_config()
    speak(
        "Done! Ready when you are.",
        voice=config["voice"],
        speed=config["speed"],
        lang=config["lang"],
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
