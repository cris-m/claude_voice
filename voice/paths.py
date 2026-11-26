"""Where the plugin keeps state.

Claude Code installs each plugin version into a fresh cache directory, so
anything written under the plugin root is lost on update. The virtualenv and
the user's config therefore live in ${CLAUDE_PLUGIN_DATA}, which persists
across updates. Outside Claude Code (e.g. a dev checkout run by hand) the
variable is unset and the plugin root is used instead.

Standard library only: hooks import this with the system Python.
"""

import json
import os
import shutil
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(PLUGIN_ROOT, "voice_config.json")


def data_dir() -> str:
    path = os.environ.get("CLAUDE_PLUGIN_DATA") or PLUGIN_ROOT
    os.makedirs(path, exist_ok=True)
    return path


def venv_python() -> str:
    venv = os.path.join(data_dir(), ".venv")
    if sys.platform == "win32":
        return os.path.join(venv, "Scripts", "python.exe")
    return os.path.join(venv, "bin", "python")


def config_path() -> str:
    """The user's config, created from the bundled defaults on first use."""
    path = os.path.join(data_dir(), "voice_config.json")
    if not os.path.exists(path):
        shutil.copyfile(DEFAULT_CONFIG_PATH, path)
    return path


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def read_config() -> dict:
    """Bundled defaults overlaid (deeply) with the user's config.

    Settings added in a newer plugin version get their defaults even though the
    user's file predates them. Legacy `messages.<name>` keys are folded into
    `follow_ups.<name>.message` unless that is set explicitly.
    """
    with open(DEFAULT_CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    try:
        with open(config_path(), encoding="utf-8") as f:
            user = json.load(f)
        if not isinstance(user, dict):
            user = {}
    except (OSError, ValueError):
        user = {}

    legacy = user.get("messages")
    if isinstance(legacy, dict):
        follow_ups = dict(user.get("follow_ups") or {})
        for name, message in legacy.items():
            entry = dict(follow_ups.get(name) or {})
            entry.setdefault("message", message)
            follow_ups[name] = entry
        user = {**user, "follow_ups": follow_ups}

    return _deep_merge(config, user)


def state_dir() -> str:
    """Private runtime state: locks, speaker registry, hook timestamps, logs.

    Kept under the data dir (not the shared system temp dir) so other local
    users can't read it or plant files in it.
    """
    path = os.path.join(data_dir(), "state")
    os.makedirs(path, mode=0o700, exist_ok=True)
    return path


class FileLock:
    """An OS-level exclusive lock on a file.

    The OS drops the lock when the holding process dies, so a crashed or
    killed speaker can never leave a stale lock behind, and no PID checks
    are needed to recover from one.
    """

    def __init__(self, path: str):
        self.path = path
        self._fd = None

    def try_acquire(self) -> bool:
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(fd)
            return False
        self._fd = fd
        return True

    def acquire(self, poll: float = 0.05) -> None:
        # Polling (rather than a blocking call) keeps the wait interruptible
        # by signals on every platform.
        import time
        while not self.try_acquire():
            time.sleep(poll)

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            if sys.platform == "win32":
                import msvcrt
                os.lseek(self._fd, 0, os.SEEK_SET)
                msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fd, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(self._fd)
        self._fd = None

    @property
    def fd(self):
        return self._fd

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
