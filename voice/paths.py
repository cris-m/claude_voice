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


def read_config() -> dict:
    """Bundled defaults overlaid with the user's config.

    Merging one level deep means settings added in a newer plugin version get
    their defaults even though the user's file predates them.
    """
    with open(DEFAULT_CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    try:
        with open(config_path(), encoding="utf-8") as f:
            user = json.load(f)
    except (OSError, ValueError):
        user = {}
    for key, value in user.items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            config[key] = {**config[key], **value}
        else:
            config[key] = value
    return config
