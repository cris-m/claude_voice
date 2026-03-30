# Claude Voice

Text-to-speech for Claude Code — hear responses, notifications, and command completions spoken aloud.

---

## What Is This?

Claude Voice adds audio feedback to Claude Code:

- **Response summaries** — Claude speaks a summary of what it did
- **Notifications** — Claude speaks when it needs your attention
- **Command completion** — Hear when long-running terminal commands finish
- **Idle alerts** — Get notified if you've been away after Claude finishes

Supports three TTS providers:

| Provider | Best for | Platform | Download |
|----------|----------|----------|----------|
| **Kokoro** | Lightweight, fast notifications | All (macOS/Windows/Linux) | ~100MB |
| **Chatterbox** | High quality, emotion, voice cloning | All (GPU recommended) | ~1GB |
| **MLX-Audio** | Fastest on Apple Silicon, emotion control | macOS Apple Silicon only | ~1.4GB |

---

## Project Structure

```
claude_voice/
├── commands/
│   ├── init.md              # /claude-voice:init
│   ├── config.md            # /claude-voice:config
│   └── tts-summary.md       # /claude-voice:tts-summary
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── check_init.py
│   ├── inject_tts_instruction.py
│   ├── record_command_start.py
│   ├── speak.py
│   ├── speak_command_done.py
│   ├── speak_idle_done.py
│   ├── speak_notification.py
│   ├── speak_summary.py
│   └── debug_hook.py
├── voice/
│   ├── __init__.py          # Provider factory
│   ├── base.py              # Abstract base class + audio locking
│   ├── kokoro_tts.py         # Kokoro ONNX provider
│   ├── chatterbox_tts.py     # Chatterbox provider
│   ├── mlx_tts.py            # MLX-Audio provider
│   └── utils.py
├── pyproject.toml
├── voice_config.json
└── README.md
```

---

## Installation

### Prerequisites

- Claude Code 1.0.33+
- Python 3.11+ (3.12+ for Kokoro)
- macOS, Windows, or Linux with audio output

### From GitHub

```
/plugin marketplace add cris-m/claude_voice
/plugin install claude-voice@cris-m-claude_voice
/claude-voice:init
```

### From local clone

```bash
git clone https://github.com/cris-m/claude_voice.git
```

```
/plugin marketplace add /path/to/claude_voice
/plugin install claude-voice@cris-m-claude_voice --scope local
/claude-voice:init
```

### For development

```bash
claude --plugin-dir /path/to/claude_voice
```

---

## Setup

### 1. Initialize (required)

```
/claude-voice:init
```

This detects your platform, lets you choose a provider, creates `.venv`, and installs dependencies. On Apple Silicon, it recommends MLX-Audio automatically.

### 2. Configure voice (optional)

```
/claude-voice:config
```

Interactive wizard for speaker, style, speed, and notification messages.

### 3. Enable spoken summaries (optional)

```
/claude-voice:tts-summary
```

---

## Configuration

All settings in `voice_config.json`:

```json
{
  "provider": "kokoro",
  "tts_summary_enabled": true,
  "messages": {
    "command_done": "All finished! What's next?",
    "idle_done": "Just a heads up, everything's wrapped up on my end. Take your time!"
  },
  "kokoro": {
    "voice": "am_michael",
    "speed": 1.2,
    "lang": "en-us"
  },
  "chatterbox": {
    "model_variant": "original",
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 0.8,
    "audio_prompt_path": null
  },
  "mlx": {
    "model": "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16",
    "voice": "Ryan",
    "language": "en",
    "instruct": "warm"
  }
}
```

Each provider has its own block. Only the active provider's block is used.

### MLX-Audio settings

| Setting | Description |
|---------|-------------|
| `model` | HuggingFace model ID |
| `voice` | Speaker: `Ryan` (clear) or `Aiden` (expressive) |
| `language` | Language code |
| `instruct` | Voice style — any natural description (e.g. `"warm"`, `"enthusiastic and energetic"`, `"calm, clear, professional"`) |

### Chatterbox settings

| Setting | Range | Description |
|---------|-------|-------------|
| `model_variant` | `original` / `turbo` | Turbo auto-falls back to original on Apple Silicon |
| `exaggeration` | 0.0–2.0 | Emotion intensity |
| `cfg_weight` | 0.0–1.0 | Voice adherence |
| `temperature` | 0.0–5.0 | Randomness |
| `audio_prompt_path` | path or null | WAV file for voice cloning |

### Kokoro settings

| Setting | Description |
|---------|-------------|
| `voice` | Voice ID (e.g. `am_michael`, `af_heart`) |
| `speed` | Speech speed (0.8–1.5) |
| `lang` | Language code (`en-us`, `en-gb`, `ja`, `zh`, `fr`, `es`, `hi`, `it`, `pt`) |

---

## Hooks

| Hook | What it does |
|------|-------------|
| SessionStart | Checks `.venv` exists, reminds to run `/claude-voice:init` |
| InstructionsLoaded | Injects TTS summary instruction (survives context compression) |
| Notification | Speaks notification messages |
| PreToolUse (Bash) | Records command start time |
| PostToolUse (Bash) | Speaks notification after commands 30s+ |
| Stop | Extracts and speaks TTS_SUMMARY from responses |
| Stop (idle) | Alerts after 60s idle post-completion |

---

## Troubleshooting

### No audio

1. Check system volume
2. Run `/claude-voice:init` if not done
3. Check `<tempdir>/speak_summary_error.log`

### Wrong voice / old config

The plugin cache may have a stale `voice_config.json`. After changing config, sync it:

```bash
cp voice_config.json ~/.claude/plugins/cache/cris-m-claude_voice/claude-voice/*/voice_config.json
```

### Test manually

```bash
.venv/bin/python scripts/speak.py "Hello, testing voice."
```

---

## Uninstall

```
/plugin uninstall claude-voice@cris-m-claude_voice
```

---

## License

MIT

---

## Credits

- **Kokoro TTS** — ONNX text-to-speech engine
- **Chatterbox** — Emotion-aware TTS by Resemble AI
- **MLX-Audio** — Apple MLX framework TTS with Qwen3-TTS
- **Claude Code** — AI coding assistant by Anthropic
