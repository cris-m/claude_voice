#!/usr/bin/env python3
"""Run a plugin script with the plugin's virtualenv Python.

    run_hook.py [--data DIR] SCRIPT.py [ARGS...]

Hooks call this with the system Python. --data sets CLAUDE_PLUGIN_DATA for
callers that don't have it in their environment (skills and commands, where
Claude Code only substitutes it into the text). This is also the one
cross-platform entry point: it finds .venv/bin/python or .venv\\Scripts\\python.exe.
"""

import os
import re
import signal
import subprocess
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PLUGIN_ROOT)


def main():
    args = sys.argv[1:]
    explicit_data = args[:1] == ["--data"]
    if explicit_data and len(args) >= 2:
        os.environ["CLAUDE_PLUGIN_DATA"] = args[1]
        args = args[2:]
    if not args:
        sys.exit(1)

    from voice.paths import venv_python

    script_name = args[0]
    if not re.match(r'^[a-zA-Z0-9_\-]+\.py$', script_name):
        sys.exit(1)

    scripts_dir = os.path.join(PLUGIN_ROOT, "scripts")
    script_path = os.path.join(scripts_dir, script_name)
    if not os.path.realpath(script_path).startswith(os.path.realpath(scripts_dir)):
        sys.exit(1)
    if not os.path.isfile(script_path):
        sys.exit(1)

    python_path = venv_python()
    if not os.path.isfile(python_path):
        if explicit_data:
            print("Voice Summary is not initialized. Run /voice-summary:init first.", file=sys.stderr)
        sys.exit(1)

    # The child inherits stdin and reads it only if it needs to: reading it
    # here would block forever when nothing is piped in (e.g. `speak.py --stop`).
    child = subprocess.Popen([python_path, script_path] + args[1:])

    # When Claude Code times out a hook it terminates this process; pass that
    # on so the child doesn't linger.
    def forward(signum, _frame):
        try:
            child.send_signal(signum)
        except OSError:
            pass
        sys.exit(128 + signum)

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, forward)

    sys.exit(child.wait())


if __name__ == "__main__":
    main()
