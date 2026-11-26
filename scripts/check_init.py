#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.paths import venv_python

if not os.path.isfile(venv_python()):
    print("Voice Summary is not initialized yet. Run /voice-summary:init to install dependencies and enable voice hooks.")
