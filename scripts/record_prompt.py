#!/usr/bin/env python3
"""UserPromptSubmit hook: note when the user last sent a message.

Runs with the system Python (standard library only) so it stays fast.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.paths import state_dir

if __name__ == "__main__":
    try:
        now = str(time.time())
        for name in ("last_prompt", "last_activity"):
            with open(os.path.join(state_dir(), name), "w") as f:
                f.write(now)
    except Exception:
        pass
