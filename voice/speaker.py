"""Background speakers: start them detached, track them, stop them.

Every speaker process registers itself by holding a lock on its own file in
state/speakers/. Holding the lock proves the process is alive and is one of
ours, so --stop never signals a stale or reused PID.

Pausing is cooperative: --pause creates state/paused, and the playing speaker
checks for it between ~100ms slices of audio (see base._SlicePlayer), holding
its place until --resume removes it.
"""

import os
import signal
import subprocess
import sys
import tempfile
import time

from .paths import PLUGIN_ROOT, FileLock, data_dir, state_dir

SPEAK_SCRIPT = os.path.join(PLUGIN_ROOT, "scripts", "speak.py")
LAST_SUMMARY_FILE = "last_summary_spoken"
PAUSED_FILE = "paused"


def _speakers_dir() -> str:
    path = os.path.join(state_dir(), "speakers")
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path


def _queue_dir() -> str:
    path = os.path.join(state_dir(), "queue")
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path


class Registration:
    """Context manager: registers the current process as a live speaker."""

    def __enter__(self):
        self._path = os.path.join(_speakers_dir(), f"{os.getpid()}.lock")
        self._lock = FileLock(self._path)
        if self._lock.try_acquire():
            os.ftruncate(self._lock.fd, 0)
            os.write(self._lock.fd, str(os.getpid()).encode())
        return self

    def __exit__(self, *exc):
        self._lock.release()
        try:
            os.remove(self._path)
        except OSError:
            pass
        # A pause outlives nothing: once the last speaker is gone, clear it so
        # the next speech doesn't start out paused.
        if not live_speakers():
            _clear_pause()


def mark_summary_spoken() -> None:
    with open(os.path.join(state_dir(), LAST_SUMMARY_FILE), "w") as f:
        f.write(str(time.time()))


def last_summary_spoken() -> float:
    try:
        with open(os.path.join(state_dir(), LAST_SUMMARY_FILE)) as f:
            return float(f.read().strip())
    except (OSError, ValueError):
        return 0.0


def speak_detached(text: str, summary: bool = False) -> None:
    """Speak in a separate process and return immediately.

    Hook timeouts then can't cut speech off, and a long summary never blocks
    the session.
    """
    fd, path = tempfile.mkstemp(dir=_queue_dir(), suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    spawn_file(path, summary=summary)


def spawn_file(path: str, summary: bool = False) -> None:
    args = [sys.executable, SPEAK_SCRIPT, "--file", path]
    if summary:
        args.append("--summary")
    env = dict(os.environ, CLAUDE_PLUGIN_DATA=data_dir())
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(
        args,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **kwargs,
    )


def live_speakers() -> list:
    """PIDs of live speakers other than this process (stale entries removed)."""
    pids = []
    directory = _speakers_dir()
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        probe = FileLock(path)
        if probe.try_acquire():
            # Nobody holds it: the speaker is gone. Clean up, don't signal.
            probe.release()
            try:
                os.remove(path)
            except OSError:
                pass
            continue
        try:
            with open(path) as f:
                pid = int(f.read().strip())
        except (OSError, ValueError):
            continue
        if pid != os.getpid():
            pids.append(pid)
    return pids


def stop_all() -> int:
    """Stop every live speaker (playing or waiting). Returns how many."""
    _clear_pause()
    stopped = 0
    for pid in live_speakers():
        try:
            os.kill(pid, signal.SIGTERM)
            stopped += 1
        except OSError:
            pass
    return stopped


def _paused_path() -> str:
    return os.path.join(state_dir(), PAUSED_FILE)


def _clear_pause() -> None:
    try:
        os.remove(_paused_path())
    except OSError:
        pass


def is_paused() -> bool:
    return os.path.exists(_paused_path())


def pause_all() -> int:
    """Pause playback. Returns how many speakers are live (0: nothing to pause)."""
    count = len(live_speakers())
    if count:
        with open(_paused_path(), "w") as f:
            f.write(str(time.time()))
    return count


def resume_all() -> bool:
    """Resume paused playback. Returns whether anything was paused."""
    was_paused = is_paused()
    _clear_pause()
    return was_paused
