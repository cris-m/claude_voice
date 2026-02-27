---
description: Create .venv and install Python packages required for voice hooks
allowed-tools: [Bash, Read, Glob]
---

# Initialize Claude Voice

Create the Python virtual environment and install all required packages. This must run once after installing the plugin — hooks will not work until this completes.

---

## What this does

1. Creates `.venv` at the plugin root
2. Installs core dependencies: `kokoro-onnx`, `numpy`, `sounddevice`
3. Speaks a test message to confirm everything works

---

## Instructions

### 1. Create .venv and install packages

**Preferred — using uv** (fast, handles venv creation automatically):
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && uv sync
```

**Fallback — using pip:**
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python3 -m venv .venv && .venv/bin/pip install -e .
```

If `sounddevice` fails to build on macOS, install PortAudio first:
```bash
brew install portaudio
```

### 2. Verify

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/speak.py" "Initialization complete. Voice is ready."
```

You should hear the message spoken aloud. If not, check your system volume.

---

## What this enables

Once `.venv` exists, all hooks defined in `hooks/hooks.json` become active:

| Hook | Script | What it does |
|------|--------|--------------|
| Notification | `speak_notification.py` | Speaks notification messages aloud |
| PostToolUse (Bash) | `speak.py` | Announces "Done! Ready when you are." after shell commands |
| Stop | `speak_summary.py` | Extracts and speaks TTS_SUMMARY from responses |

---

## Next steps

- Run `/claude-voice:config` to choose your voice, speed, and language
- Run `/claude-voice:tts-summary` to enable spoken summaries
