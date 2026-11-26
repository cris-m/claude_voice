#!/usr/bin/env python3
"""Speak text aloud.

    speak.py "some text"        speak the arguments (blocks until done)
    speak.py < file             speak stdin (blocks until done)
    speak.py --detach < file    speak stdin in a background process and return at once
    speak.py --stop             stop whatever is currently being spoken
"""

import os
import signal
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice import TEMP_DIR

PID_FILE = os.path.join(TEMP_DIR, "claude_voice_speak.pid")


def _stop() -> None:
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass


def _speak(text: str) -> None:
    text = text.strip()
    if not text:
        return
    # Turn SIGTERM (from --stop) into a normal exit so the audio lock is released.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    try:
        from voice import speak
        speak(text)
    finally:
        try:
            with open(PID_FILE) as f:
                if f.read().strip() == str(os.getpid()):
                    os.remove(PID_FILE)
        except OSError:
            pass


def _detach(text: str) -> None:
    fd, path = tempfile.mkstemp(prefix="claude_voice_", suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--file", path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--stop"]:
        _stop()
    elif args[:1] == ["--detach"]:
        _detach(sys.stdin.read())
    elif args[:1] == ["--file"] and len(args) > 1:
        with open(args[1], encoding="utf-8") as f:
            text = f.read()
        os.remove(args[1])
        _speak(text)
    elif args:
        _speak(" ".join(args))
    else:
        _speak(sys.stdin.read())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
