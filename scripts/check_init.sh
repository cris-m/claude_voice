#!/bin/sh
# SessionStart hook: check if .venv exists and remind user to initialize if not.
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "$PLUGIN_ROOT/.venv/bin/python" ]; then
    echo "Claude Voice is not initialized yet. Run /claude-voice:init to install dependencies and enable voice hooks."
fi
