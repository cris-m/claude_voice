#!/usr/bin/env python3

import os
import sys

plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    python_path = os.path.join(plugin_root, ".venv", "Scripts", "python.exe")
else:
    python_path = os.path.join(plugin_root, ".venv", "bin", "python")

if not os.path.isfile(python_path):
    print("Claude Voice is not initialized yet. Run /claude-voice:init to install dependencies and enable voice hooks.")
