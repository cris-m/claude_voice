#!/usr/bin/env python3

import sys
import os
import json
import tempfile
from datetime import datetime

DEBUG_FILE = os.path.join(tempfile.gettempdir(), "claude_hook_debug.json")

def main():
    try:
        input_data = sys.stdin.read().strip()
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "raw_input": input_data,
            "parsed": None,
            "error": None
        }
        if input_data:
            try:
                debug_info["parsed"] = json.loads(input_data)
            except json.JSONDecodeError as e:
                debug_info["error"] = f"JSON parse error: {e}"

        with open(DEBUG_FILE, "a") as f:
            f.write(json.dumps(debug_info, indent=2, default=str))
            f.write("\n---\n")
    except Exception as e:
        with open(DEBUG_FILE, "a") as f:
            f.write(f"Error: {e}\n---\n")

if __name__ == "__main__":
    main()
