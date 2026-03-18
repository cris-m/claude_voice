#!/usr/bin/env python3

import sys
import os
import json
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import TEMP_DIR

STAMP_DIR = os.path.join(TEMP_DIR, "claude_voice_cmd_times")
THRESHOLD_SECONDS = 30


def main():
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    data = json.loads(input_data)
    tool_use_id = data.get("tool_use_id", "")
    if not tool_use_id or not re.match(r'^[a-zA-Z0-9_\-]+$', tool_use_id):
        return

    stamp_file = os.path.join(STAMP_DIR, tool_use_id)

    try:
        with open(stamp_file, "r") as f:
            start_time = float(f.read().strip())
    except (FileNotFoundError, ValueError):
        return
    finally:
        # Clean up regardless
        try:
            os.remove(stamp_file)
        except OSError:
            pass

    elapsed = time.time() - start_time
    if elapsed < THRESHOLD_SECONDS:
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
