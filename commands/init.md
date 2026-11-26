---
description: Create the virtualenv and install Python packages required for voice hooks
allowed-tools: [Bash, Read, Glob, Write, Edit, AskUserQuestion]
---

# Initialize Voice Summaries

Create the Python virtual environment and install all required packages. This must run once after installing the plugin — hooks will not work until this completes.

---

## Instructions

## Where things live

- `${CLAUDE_PLUGIN_ROOT}`: the plugin's code. It is replaced on every plugin update, so **never write to it**.
- `${CLAUDE_PLUGIN_DATA}`: persistent data that survives updates. The virtualenv is `${CLAUDE_PLUGIN_DATA}/.venv` and the user's settings are `${CLAUDE_PLUGIN_DATA}/voice_config.json`. If that config file doesn't exist yet, copy `${CLAUDE_PLUGIN_ROOT}/voice_config.json` there first, then read or edit the copy.


### Step 1: Detect platform and ask provider

First, detect the platform:
```bash
python3 -c "import sys, platform; print(sys.platform, platform.machine())"
```

Based on the output, present providers with smart recommendations:

- If `darwin arm64` (macOS Apple Silicon): show all 3, recommend **MLX-Audio**
- If `darwin x86_64` (macOS Intel): show Kokoro and Chatterbox only, recommend **Kokoro**
- If `linux` or `win32`: show Kokoro and Chatterbox only
  - Recommend **Kokoro** for general use (lightweight, fast)
  - Mention **Chatterbox** for users with a GPU who want higher quality

**Provider descriptions:**

- **Kokoro** — Lightweight ONNX engine, 54 voices across 8 languages, fast startup. ~100MB download. Requires Python 3.12+.
- **Chatterbox** — High-quality engine by Resemble AI, emotion control, voice cloning from 10s audio. ~1GB download (PyTorch). Requires Python 3.11.
- **MLX-Audio** (macOS Apple Silicon only) — Native Apple MLX framework, Qwen3-TTS with emotion control, fastest inference on M-series chips. ~1.4GB download (cached after first use). Requires Python 3.10+.

### Step 2: Create the virtualenv and install

The virtualenv goes in the plugin's persistent data directory, `${CLAUDE_PLUGIN_DATA}/.venv`, so it survives plugin updates. Only the dependencies are installed; the plugin's own code is always loaded from `${CLAUDE_PLUGIN_ROOT}`. If a `.venv` already exists there, recreate it when switching providers.

**IMPORTANT:** Use `uv pip install` (not `uv sync`) because the Kokoro and Chatterbox extras have conflicting numpy versions. `uv sync` resolves all extras together and will fail.

Set `EXTRA` to `kokoro`, `chatterbox` or `mlx`, and `PYVER` to `3.12` for Kokoro, `3.11` for Chatterbox, or `3.12` for MLX:

```bash
uv venv --clear --python "$PYVER" "${CLAUDE_PLUGIN_DATA}/.venv" && uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" -r "${CLAUDE_PLUGIN_ROOT}/pyproject.toml" --extra "$EXTRA"
```

For MLX, also run:
```bash
uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" --upgrade mlx-audio mlx-lm numpy transformers
```

Pip fallback if `uv` isn't available (macOS/Linux; on Windows use `Scripts\pip`). This installs a copy of the package as well, which is harmless because the scripts load the code from the plugin root first:
```bash
python3 -m venv "${CLAUDE_PLUGIN_DATA}/.venv" && "${CLAUDE_PLUGIN_DATA}/.venv/bin/pip" install "${CLAUDE_PLUGIN_ROOT}[$EXTRA]"
```

If `sounddevice` fails on macOS: `brew install portaudio`

### Step 3: Save provider choice to config

Update the `provider` field in `${CLAUDE_PLUGIN_DATA}/voice_config.json` (copy it from `${CLAUDE_PLUGIN_ROOT}/voice_config.json` first if it doesn't exist) and write it back. The file already contains defaults for all providers.

### Step 4: Verify

Run the test speak script:
```bash
CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_DATA}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/speak.py" "Initialization complete. Voice is ready."
```

**This test will also trigger the model download** — so it may take a few minutes the first time. That is expected. Wait until you hear the audio before proceeding.

| Provider | Download size | Where cached |
|----------|--------------|--------------|
| Kokoro | ~100MB | `~/.cache/kokoro-onnx/` |
| Chatterbox | ~1GB | `~/.cache/huggingface/hub/` |
| MLX-Audio | ~1.4GB | `~/.cache/huggingface/hub/` |

After the download completes once, all future calls load from local cache in 2-3 seconds.

---

## What this enables

Once the virtualenv exists, all hooks defined in `hooks/hooks.json` become active:

| Hook | Script | What it does |
|------|--------|--------------|
| Notification | `speak_notification.py` | Speaks notification messages aloud |
| PreToolUse (Bash) | `record_command_start.py` | Records when a command starts |
| PostToolUse (Bash) | `speak_command_done.py` | Speaks a follow-up after long commands (configurable) |
| Stop | `speak_summary.py` | Extracts and speaks TTS_SUMMARY from responses |
| Stop | `speak_idle_done.py` | Speaks a follow-up if you've been away after Claude finishes (configurable) |

---

## Next steps

- Run `/voice-summaries:config` to choose your voice, speed, and language
- Run `/voice-summaries:speak` (or ask "give me a voice summary") for a one-off spoken summary
- Run `/voice-summaries:tts-summary` to speak a summary after every response
