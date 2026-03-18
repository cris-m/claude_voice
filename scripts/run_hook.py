#!/usr/bin/env python3

import os
import re
import subprocess
import sys


def _venv_python() -> str:
    """Return the path to the venv Python executable, platform-aware."""
    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if sys.platform == "win32":
        return os.path.join(plugin_root, ".venv", "Scripts", "python.exe")
    return os.path.join(plugin_root, ".venv", "bin", "python")


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    script_name = sys.argv[1]

    if not re.match(r'^[a-zA-Z0-9_\-]+\.py$', script_name):
        sys.exit(1)

    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(plugin_root, "scripts")
    script_path = os.path.join(scripts_dir, script_name)

    if not os.path.realpath(script_path).startswith(os.path.realpath(scripts_dir)):
        sys.exit(1)

    if not os.path.isfile(script_path):
        sys.exit(1)

    python_path = _venv_python()
    if not os.path.isfile(python_path):
        sys.exit(1)

    result = subprocess.run(
        [python_path, script_path],
        input=sys.stdin.buffer.read(),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
