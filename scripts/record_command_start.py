#!/usr/bin/env python3

import sys
import os
import json
import re
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.paths import state_dir

STAMP_DIR = os.path.join(state_dir(), "cmd_times")
ACTIVITY_FILE = os.path.join(state_dir(), "last_activity")


def _safe_id(tool_use_id: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_\-]+$', tool_use_id))


def main():
    input_data = sys.stdin.read().strip()
    if not input_data:
        return

    data = json.loads(input_data)
    tool_use_id = data.get("tool_use_id", "")
    if not tool_use_id or not _safe_id(tool_use_id):
        return

    now = str(time.time())

    os.makedirs(STAMP_DIR, mode=0o700, exist_ok=True)

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
