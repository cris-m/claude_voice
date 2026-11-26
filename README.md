# Voice Summary

Text-to-speech for Claude Code — hear responses, notifications, and command completions spoken aloud.

> Fork of [cris-m/claude_voice](https://github.com/cris-m/claude_voice) that adds on-demand voice summaries with selectable length, streaming playback, and configurable follow-up messages.

---

## What Is This?

Voice Summary adds audio feedback to Claude Code:

- **Voice summaries on demand** — ask for a spoken summary when you want one, from a one-liner to a podcast-style walkthrough
- **Always-on summaries** (optional) — Claude speaks a summary after every response
- **Streaming playback** — speech starts while the rest is still being generated (Kokoro, MLX-Audio)
- **Notifications** — Claude speaks when it needs your attention
- **Command completion** — Hear when long-running terminal commands finish
- **Idle alerts** — Get notified if you've been away after Claude finishes

Notifications, command completion and idle alerts are *follow-ups*: each can be turned on or off, with its own message and timing.

Supports three TTS providers:

| Provider | Best for | Platform | Download |
|----------|----------|----------|----------|
| **Kokoro** | Lightweight, fast notifications | All (macOS/Windows/Linux) | ~100MB |
| **Chatterbox** | High quality, emotion, voice cloning | All (GPU recommended) | ~1GB |
| **MLX-Audio** | Fastest on Apple Silicon, emotion control | macOS Apple Silicon only | ~1.4GB |

---

## Project Structure

```
voice-summary/
├── commands/
│   ├── init.md              # /voice-summary:init
│   ├── config.md            # /voice-summary:config
│   └── tts-summary.md       # /voice-summary:tts-summary (always-on)
├── skills/
│   └── speak/
│       └── SKILL.md         # /voice-summary:speak, or "give me a voice summary"
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── check_init.py
│   ├── inject_tts_instruction.py
│   ├── record_command_start.py
│   ├── run_hook.py          # Runs a script with the venv Python (all platforms)
│   ├── record_prompt.py     # Notes when you last sent a message
│   ├── speak.py             # speak text; --detach / --pause / --resume / --stop
│   ├── speak_command_done.py
│   ├── speak_idle_done.py
│   ├── speak_notification.py
│   ├── speak_summary.py
│   └── debug_hook.py
├── voice/
│   ├── __init__.py          # Provider factory
│   ├── base.py              # Abstract base class, streaming playback, audio locking
│   ├── lengths.py           # Summary length definitions (short … podcast)
│   ├── kokoro_tts.py         # Kokoro ONNX provider
│   ├── chatterbox_tts.py     # Chatterbox provider
│   ├── mlx_tts.py            # MLX-Audio provider
│   ├── paths.py             # Data/state dirs, config loading, OS file locks
│   ├── speaker.py           # Background speakers: start, track, pause, stop
│   └── utils.py
├── tools/
│   └── release.py           # Bump version, commit, tag vX.Y.Z
├── .github/workflows/
│   └── release.yml          # On tag push: check version, validate, create GitHub release
├── pyproject.toml
├── voice_config.json        # Default settings (copied to your data dir on first use)
└── README.md
```

---

## Installation

### Prerequisites

- Claude Code 1.0.33+
- Python 3.11+ (3.12+ for Kokoro)
- macOS, Windows, or Linux with audio output
- `python3` on your PATH (hooks and the skill call it to launch the plugin's own virtualenv)

### From GitHub

```
/plugin marketplace add havekes/voice-summary
/plugin install voice-summary@havekes
/voice-summary:init
```

### From local clone

```bash
git clone https://github.com/havekes/voice-summary.git
```

```
/plugin marketplace add /path/to/voice-summary
/plugin install voice-summary@havekes --scope local
/voice-summary:init
```

### For development

```bash
claude --plugin-dir /path/to/voice-summary
```

---

## Setup

### 1. Initialize (required)

```
/voice-summary:init
```

This detects your platform, lets you choose a provider, creates a virtualenv in the plugin's data directory, and installs dependencies. On Apple Silicon, it recommends MLX-Audio automatically.

### 2. Configure voice (optional)

```
/voice-summary:config
```

Interactive wizard for speaker, style, speed, default summary length, streaming, and follow-up messages.

### 3. Voice summaries on demand

```
/voice-summary:speak [short|medium|long|podcast] [what to cover]
/voice-summary:speak pause
/voice-summary:speak resume
/voice-summary:speak stop
```

Each invocation speaks one summary, by default of Claude's latest response; add words after the length to choose what it covers. Because it's a skill, you can also just ask: "give me a quick voice summary", "talk me through the refactor, podcast style", "hold on", "keep going", "be quiet". Pause keeps your place in the current speech (anything queued behind it waits too); stop discards it. Audio plays in the background, so even a podcast doesn't block the conversation.

| Length | Roughly |
|--------|---------|
| `short` | 1-2 sentences, ~15s |
| `medium` | 3-6 sentences, ~45s (default) |
| `long` | 2-4 paragraphs, 1.5-3 min |
| `podcast` | single-host segment, 4-8 min |

With no length given, `summary_length` from the config is used. Claude writes the script and hands it to the speaker in a background process, then replies with a single line. The script isn't repeated in the chat.

### 4. Always-on summaries (optional)

```
/voice-summary:tts-summary [on|off]
```

Ends every response with a spoken summary at `summary_length`. Off by default in this fork (`tts_summary_enabled: false`); turning it off takes effect immediately, since the Stop hook checks the flag before speaking.

---

## Configuration

Your settings live in `~/.claude/plugins/data/<plugin-id>/voice_config.json` (Claude Code's `${CLAUDE_PLUGIN_DATA}` directory), next to the plugin's virtualenv. That directory survives plugin updates, unlike the plugin's install folder. It's created from the bundled defaults the first time the plugin runs. Settings added in later versions take their defaults automatically, so you only need to keep what you've changed.

The full set of settings:

```json
{
  "provider": "kokoro",
  "tts_summary_enabled": false,
  "summary_length": "medium",
  "streaming": true,
  "stream_prebuffer_seconds": 0.5,
  "follow_ups": {
    "command_done": { "enabled": true, "threshold_seconds": 30, "message": "All finished! What's next?" },
    "idle_done": { "enabled": true, "threshold_seconds": 60, "message": "Just a heads up, everything's wrapped up on my end. Take your time!" },
    "notification": { "enabled": true }
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
    "instruct": "warm",
    "streaming_interval": 1.0
  }
}
```

Each provider has its own block. Only the active provider's block is used.

### Top-level settings

| Setting | Default | Description |
|---------|---------|-------------|
| `provider` | `kokoro` | `kokoro`, `chatterbox` or `mlx` |
| `tts_summary_enabled` | `false` | Always-on summaries after every response |
| `summary_length` | `medium` | Default length: `short`, `medium`, `long` or `podcast` |
| `streaming` | `true` | Play audio while it is being generated, where supported |
| `stream_prebuffer_seconds` | `0.5` | Audio queued before streamed playback starts; raise it if speech stutters on a slower machine |
| `follow_ups` | all on | See below |

### Streaming

With `"streaming": true` (the default), audio starts playing while the rest is still being generated. Kokoro and MLX-Audio support this. Chatterbox has no streaming API and always generates the full clip first. Set it to `false` to always generate the whole clip before playing.

The model generates on a background thread while audio plays, and playback starts once `stream_prebuffer_seconds` of audio is queued. If speech still stutters on a slower machine, raise the prebuffer (for example to `2.0`) or turn streaming off.

### Follow-ups

`follow_ups` controls the messages hooks speak without Claude's involvement. Each one can be turned off with `"enabled": false`.

| Key | Fires when | Notes |
|-----|-----------|-------|
| `command_done` | A Bash command ran longer than `threshold_seconds` | |
| `idle_done` | No activity for `threshold_seconds` after Claude stops, and no summary was spoken since your last message | Capped at 580s by the hook timeout |
| `notification` | Claude Code raises a notification | |

The older `messages.command_done` / `messages.idle_done` keys still work.

### MLX-Audio settings

| Setting | Description |
|---------|-------------|
| `model` | HuggingFace model ID |
| `voice` | Speaker: `Ryan` (clear) or `Aiden` (expressive) |
| `language` | Language code |
| `streaming_interval` | Seconds of audio per streamed chunk (default `1.0`); lower starts sooner |
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
| SessionStart | Checks the virtualenv exists, reminds to run `/voice-summary:init` |
| UserPromptSubmit | Records when you last sent a message (used by the idle follow-up) |
| InstructionsLoaded | When always-on summaries are enabled, injects the summary instruction at `summary_length` (survives context compression) |
| Notification | Speaks notification messages (`follow_ups.notification`) |
| PreToolUse (Bash) | Records command start time |
| PostToolUse (Bash) | Speaks `command_done` after long commands |
| Stop | Extracts and speaks TTS_SUMMARY from responses (only when always-on summaries are enabled) |
| Stop (idle) | Speaks `idle_done` after a period of inactivity |

All speech from hooks plays in a background process, so a hook timeout never cuts a sentence off and a podcast-length summary doesn't hold anything up. On-demand summaries don't go through a hook: the `speak` skill calls `speak.py --detach` directly, and is pre-approved to run only that one command.

Runtime state (the audio lock, running speakers, hook timestamps and logs) lives in a private `state/` folder inside the data directory, not in the shared system temp folder.

---

## Troubleshooting

### No audio

1. Check system volume
2. Run `/voice-summary:init` if not done
3. Check `state/speak_summary_error.log` in the plugin data directory

### Speech won't stop / something is stuck

Run `/voice-summary:speak stop`. It stops everything that is playing or waiting to play. Speakers take turns using an operating-system file lock, which is released automatically if a speaker crashes, so nothing can get stuck holding it.

### Settings or install lost after an update

They shouldn't be: both live in the persistent data directory. If you previously used the original plugin, its `.venv` and `voice_config.json` were inside the install folder and were not carried over. Run `/voice-summary:init` once, then `/voice-summary:config`.

### Test manually

From a development clone (without `CLAUDE_PLUGIN_DATA` set, the venv and config are read from the clone itself):

```bash
python3 scripts/run_hook.py speak.py "Hello, testing voice."
echo "Long text..." | python3 scripts/run_hook.py speak.py --detach   # background
python3 scripts/run_hook.py speak.py --stop
```

---

## Releasing

Claude Code reads the version from `.claude-plugin/plugin.json` and only offers users an update when it changes. Releases are git tags that always match that version:

```bash
python3 tools/release.py 0.3.0 --push
```

The script must run on a clean `main`. It sets the version in `plugin.json` and `pyproject.toml`, commits, creates the `v0.3.0` tag, and pushes both. When the tag lands, the release workflow checks that it matches `plugin.json`, runs `claude plugin validate`, and creates a GitHub release with generated notes.

Users get the update with `/plugin` → Update, or `claude plugin update voice-summary@havekes`. To stay on a specific release, add the marketplace at its tag: `/plugin marketplace add havekes/voice-summary#v0.3.0`.

### Anthropic plugin directory

Run `claude plugin validate --strict .`, then submit through the developer portal at https://claude.ai/directory/manage (requires a paid claude.ai plan).

---

## Uninstall

```
/plugin uninstall voice-summary@havekes
```

---

## License

MIT

---

## Credits

- **[cris-m/claude_voice](https://github.com/cris-m/claude_voice)** — the original plugin this fork builds on
- **Kokoro TTS** — ONNX text-to-speech engine
- **Chatterbox** — Emotion-aware TTS by Resemble AI
- **MLX-Audio** — Apple MLX framework TTS with Qwen3-TTS
- **Claude Code** — AI coding assistant by Anthropic
