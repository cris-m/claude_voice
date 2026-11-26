#!/usr/bin/env python3
"""Speak text aloud.

    speak.py "some text"             speak the arguments (blocks until done)
    speak.py < file                  speak stdin (blocks until done)
    speak.py --detach < file         speak stdin in the background, return at once
    speak.py --stop                  stop everything currently being spoken
    speak.py --pause                 pause playback where it is
    speak.py --resume                resume paused playback

Add --summary to mark the speech as a summary (suppresses the idle follow-up).
"""

import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice.speaker import (
    Registration, mark_summary_spoken, pause_all, resume_all, speak_detached,
    stop_all,
)


def _speak(text: str, summary: bool) -> None:
    text = text.strip()
    if not text:
        return
    # Turn SIGTERM (from --stop) into a normal exit so locks are released and
    # audio is cut off cleanly.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    with Registration():
        if summary:
            mark_summary_spoken()
        from voice import speak
        speak(text)


def main() -> None:
    args = sys.argv[1:]
    summary = "--summary" in args
    args = [a for a in args if a != "--summary"]

    if args[:1] == ["--stop"]:
        stop_all()
    elif args[:1] == ["--pause"]:
        print("Paused." if pause_all() else "Nothing is playing.")
    elif args[:1] == ["--resume"]:
        print("Resumed." if resume_all() else "Nothing is paused.")
    elif args[:1] == ["--detach"]:
        speak_detached(sys.stdin.read(), summary=summary)
    elif args[:1] == ["--file"] and len(args) == 2:
        try:
            with open(args[1], encoding="utf-8") as f:
                text = f.read()
        finally:
            try:
                os.remove(args[1])
            except OSError:
                pass
        _speak(text, summary)
    elif args:
        _speak(" ".join(args), summary)
    else:
        _speak(sys.stdin.read(), summary)


if __name__ == "__main__":
    try:
        main()
    except (Exception, SystemExit):
        pass
    finally:
        # Cleanup (audio cut, locks released, registry entry removed) has run by
        # now. Exit at once rather than wait for a TTS worker thread to finish
        # generating audio nobody will hear.
        sys.stdout.flush()
        os._exit(0)
