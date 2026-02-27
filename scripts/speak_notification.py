#!/usr/bin/env python3

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import speak, clean_for_speech, load_config

if __name__ == "__main__":
    try:
        input_data = json.load(sys.stdin)
        message = input_data.get("message", "")
        if message:
            message = clean_for_speech(message)
            message = message.replace("Claude needs", "I need")
            message = message.replace("Claude is", "I am")
            message = message.replace("Claude", "I")
            config = load_config()
            speak(message, voice=config["voice"], speed=config["speed"], lang=config["lang"])
    except Exception:
        pass
