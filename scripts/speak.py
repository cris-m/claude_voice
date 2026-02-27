#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import speak, load_config

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        try:
            config = load_config()
            speak(text, voice=config["voice"], speed=config["speed"], lang=config["lang"])
        except Exception:
            pass
