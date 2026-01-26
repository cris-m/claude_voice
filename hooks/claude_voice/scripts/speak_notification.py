#!/usr/bin/env python3

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import speak, clean_for_speech

if __name__ == "__main__":
    try:
        input_data = json.load(sys.stdin)
        message = input_data.get("message", "")
        if message:
            message = clean_for_speech(message)
            message = message.replace("Claude needs", "I need")
            message = message.replace("Claude is", "I am")
            message = message.replace("Claude", "I")
            speak(message, voice="am_michael", speed=1.2, lang="en-us")
    except Exception:
        pass
