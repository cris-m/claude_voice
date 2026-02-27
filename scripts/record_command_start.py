#!/usr/bin/env python3

import sys
import os
import json
import time

STAMP_DIR = "/tmp/claude_voice_cmd_times"
ACTIVITY_FILE = "/tmp/claude_voice_last_activity"


def main():
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    data = json.loads(input_data)
    tool_use_id = data.get("tool_use_id", "")
    if not tool_use_id:
        return

    now = str(time.time())

    os.makedirs(STAMP_DIR, exist_ok=True)

    stamp_file = os.path.join(STAMP_DIR, tool_use_id)
    with open(stamp_file, "w") as f:
        f.write(now)

    with open(ACTIVITY_FILE, "w") as f:
        f.write(now)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
