---
description: Create .venv and install Python packages required for voice hooks
allowed-tools: [Bash, Read, Glob, Write, Edit, AskUserQuestion]
---

# Initialize Claude Voice

Create the Python virtual environment and install all required packages. This must run once after installing the plugin — hooks will not work until this completes.

---

## Instructions

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

### Step 2: Create .venv and install

**IMPORTANT:** Use `uv pip install` (not `uv sync`) because the Kokoro and Chatterbox extras have conflicting numpy versions. `uv sync` resolves all extras together and will fail.

**For Kokoro:**
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && uv venv && uv pip install -e ".[kokoro]"
```

Pip fallback (macOS/Linux):
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python3 -m venv .venv && .venv/bin/pip install -e ".[kokoro]"
```

Pip fallback (Windows):
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python -m venv .venv && .venv\Scripts\pip install -e ".[kokoro]"
```

**For Chatterbox:**
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && uv venv --python 3.11 && uv pip install -e ".[chatterbox]"
```

Pip fallback (macOS/Linux):
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python3.11 -m venv .venv && .venv/bin/pip install -e ".[chatterbox]"
```

**For MLX-Audio (macOS Apple Silicon only):**
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && uv venv && uv pip install -e ".[mlx]" && uv pip install --upgrade mlx-audio mlx-lm numpy transformers
```

Pip fallback:
```bash
cd "${CLAUDE_PLUGIN_ROOT}" && python3 -m venv .venv && .venv/bin/pip install -e ".[mlx]" && .venv/bin/pip install --upgrade mlx-audio mlx-lm numpy transformers
```

If `sounddevice` fails on macOS: `brew install portaudio`

### Step 3: Save provider choice to config

Read the existing `voice_config.json`, update the `provider` field to the chosen provider, and write it back. The file already contains defaults for all providers.

### Step 4: Verify

Run the test speak script:
```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/speak.py" "Initialization complete. Voice is ready."
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

Once `.venv` exists, all hooks defined in `hooks/hooks.json` become active:

| Hook | Script | What it does |
|------|--------|--------------|
| Notification | `speak_notification.py` | Speaks notification messages aloud |
| PreToolUse (Bash) | `record_command_start.py` | Records when a command starts |
| PostToolUse (Bash) | `speak_command_done.py` | Says "Done!" after commands that took 30+ seconds |
| Stop | `speak_summary.py` | Extracts and speaks TTS_SUMMARY from responses |
| Stop | `speak_idle_done.py` | Lets you know if you've been away 60s after Claude finishes |

---

## Next steps

- Run `/claude-voice:config` to choose your voice, speed, and language
- Run `/claude-voice:tts-summary` to enable spoken summaries
