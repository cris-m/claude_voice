# Claude Voice

Text-to-speech system for Claude Code using Kokoro TTS.

---

## What Is This?

Claude Voice adds audio feedback to Claude Code. Instead of reading the screen, you can hear:

- **Response summaries** - Claude speaks a summary of what it did or explained
- **Notifications** - Claude speaks when it needs your attention
- **Command completion** - Hear when terminal commands finish

This is useful for:

- Multitasking while Claude works
- Accessibility for visually impaired users
- Staying informed without watching the screen

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Claude writes response with hidden TTS_SUMMARY         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Response completes, Stop hook triggers                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Script reads conversation and extracts summary         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Kokoro TTS speaks the summary aloud                    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
claude_voice/
│
├── .claude-plugin/             # Plugin manifest
│   ├── plugin.json
│   └── marketplace.json
├── commands/                   # Slash commands (namespaced by plugin)
│   ├── init.md                 # Install packages and create .venv
│   ├── config.md               # Interactive voice configuration wizard
│   └── tts-summary.md          # Enable/disable TTS summaries
├── hooks/                      # Event-driven hooks (plugin-scoped)
│   └── hooks.json
├── scripts/                    # Hook scripts
│   ├── check_init.sh           # Checks if .venv exists on session start
│   ├── record_command_start.py # Records when a Bash command begins
│   ├── speak_command_done.py   # Announces completion for long commands (30s+)
│   ├── speak_idle_done.py      # Speaks up if you've been away 60s after Claude finishes
│   ├── speak.py                # Basic speech function
│   ├── speak_notification.py   # Speaks notifications
│   ├── speak_summary.py        # Extracts and speaks summaries
│   └── debug_hook.py           # Logs hook data for debugging
├── voice/                      # Kokoro TTS engine
│   ├── __init__.py
│   ├── voice.py
│   └── utils.py
├── pyproject.toml              # Python project config and dependencies
├── voice_config.json           # User-configurable voice settings
├── LICENSE                     # MIT License
└── README.md                   # This file
```

---

## Installation

This project is a Claude Code plugin. Add its marketplace, install the plugin, then initialize the Python environment.

### Prerequisites

- Claude Code 1.0.33 or later
- Python 3.12–3.13 on your machine
- macOS with audio output enabled

### Step 1: Add the Marketplace

Register the marketplace so Claude Code can discover the plugin.

**From GitHub:**
```
/plugin marketplace add cris-m/claude_voice
```

**From a local folder** (for development):
```
/plugin marketplace add /path/to/claude-voice
```

You can also run `/plugin`, go to the **Marketplaces** tab, and add it interactively.

### Step 2: Install the Plugin

```
/plugin install claude-voice@cris-m-claude_voice
```

Or run `/plugin`, go to the **Discover** tab, select **claude-voice**, and choose an installation scope (User, Project, or Local).

### Step 3: Initialize (Required)

All hooks depend on `.venv/bin/python` existing at the plugin root. **Hooks will not work until this step is completed.**

The easiest way is to use the built-in command inside Claude Code:

```
/claude-voice:init
```

This creates `.venv` and installs all dependencies (`kokoro-onnx`, `numpy`, `sounddevice`). On session start, the plugin checks if `.venv` exists and reminds you to run `/claude-voice:init` if it's missing.

**Alternatively**, install manually from your terminal:

```bash
cd ~/.claude/plugins/cache/cris-m-claude_voice/claude-voice/0.1.0
uv sync
```

If you don't have `uv`, use pip:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

If `sounddevice` fails to build on macOS, install PortAudio first:
```bash
brew install portaudio
```

### Step 4: Configure Voice (Optional)

Pick your preferred voice, speed, and language with the interactive wizard:

```
/claude-voice:config
```

Claude walks you through the choices step by step. You can skip this — the default voice is `am_michael` (American Male) at 1.2x speed.

### Step 5: Enable Spoken Summaries (Optional)

Turn on audio summaries so Claude speaks a brief overview of each response:

```
/claude-voice:tts-summary on
```

### What Gets Activated

Once installed and initialized, these hooks run automatically:

| Hook | What it does |
|------|--------------|
| SessionStart | Checks if `.venv` exists, reminds you to run `/claude-voice:init` if not |
| Notification | Speaks notification messages aloud |
| PreToolUse (Bash) | Records when a command starts |
| PostToolUse (Bash) | Says “Done! Ready when you are.” if the command took 30+ seconds |
| Stop | Extracts and speaks the TTS summary from responses |
| Stop (idle) | Lets you know if you've been away for 60s after Claude finishes |

No manual editing of `~/.claude/settings.json` is required when using plugins.

---

## Commands

The plugin provides three slash commands:

| Command | Description |
|---------|-------------|
| `/claude-voice:init` | Create `.venv` and install Python dependencies — **required before hooks work** |
| `/claude-voice:config` | Interactive wizard to choose voice, speed, and language |
| `/claude-voice:tts-summary [on\|off]` | Enable or disable spoken audio summaries of Claude responses |

---

## Usage

### Quick Start

1. Install dependencies (required once):
   ```
   /claude-voice:init
   ```
2. Configure your voice (optional):
   ```
   /claude-voice:config
   ```
   Claude walks you through picking a voice, speed, and language.
3. Enable spoken summaries:
   ```
   /claude-voice:tts-summary on
   ```
4. Try it out:
   - Run a long command (30+ seconds) — you'll hear “Done! Ready when you are.”
   - Ask Claude a question — a spoken summary plays when it finishes

### Enable Spoken Summaries

```
/claude-voice:tts-summary
```

or

```
/claude-voice:tts-summary on
```

### Disable Spoken Summaries

```
/claude-voice:tts-summary off
```

---

## Hook Configuration

Defined in [hooks/hooks.json](hooks/hooks.json):

| Hook | Matcher | Script | Async | What it does |
|------|---------|--------|-------|--------------|
| SessionStart | — | `check_init.sh` | No | Warns if `.venv` is missing |
| Notification | — | `speak_notification.py` | Yes | Speaks notification messages aloud |
| PreToolUse | `Bash` | `record_command_start.py` | No | Records when a command starts |
| PostToolUse | `Bash` | `speak_command_done.py` | Yes | Says “Done! Ready when you are.” if the command took 30+ seconds |
| Stop | — | `debug_hook.py` | Yes | Logs raw hook data to `/tmp/claude_hook_debug.json` |
| Stop | — | `speak_summary.py` | Yes | Extracts and speaks TTS_SUMMARY from responses |
| Stop | — | `speak_idle_done.py` | Yes | Lets you know if you've been away 60s after Claude finishes (skipped if summary was spoken) |

---

## How Summaries Work

When `/claude-voice:tts-summary` is enabled, Claude adds a hidden summary block:

```
<!-- TTS_SUMMARY
Your summary text here.
TTS_SUMMARY -->
```

The Stop hook:

1. Reads the conversation transcript
2. Finds the TTS_SUMMARY markers
3. Extracts the text between them
4. Cleans special characters
5. Speaks using Kokoro TTS

---

## Summary Types

Claude provides different summaries based on context:

| Type | When Used |
|------|-----------|
| Task Completion | After doing something |
| Concept Explanation | When teaching or explaining |
| Solution Proposal | When recommending options |
| Question Answer | When answering questions |
| Research Findings | After searching for information |
| Problem Explanation | When errors occur |

---

## Troubleshooting

### No Audio Playing

1. Check system volume
2. Ensure `.venv` exists in the plugin root and dependencies are installed (run `/claude-voice:init`)
3. Look at `/tmp/speak_summary_error.log`

### Summary Not Spoken

1. Run `/claude-voice:tts-summary` to enable
2. Check `/tmp/speak_summary_debug.log`
3. Verify TTS_SUMMARY markers are in response

### Debug Logs

| Log File | Contents |
|----------|----------|
| `/tmp/claude_hook_debug.json` | Raw hook data |
| `/tmp/speak_summary_debug.log` | Script execution |
| `/tmp/speak_summary_error.log` | Error messages |

### Test Manually

```bash
echo '{"transcript_path":"/path/to/transcript.jsonl"}' | \
  ./.venv/bin/python \
  ./scripts/speak_summary.py
```

---

## Voice Configuration

All voice settings are stored in `voice_config.json` at the plugin root. Edit this file to customize voice, speed, and language without touching any code.

```json
{
  "voice": "am_michael",
  "speed": 1.2,
  "lang": "en-us"
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `voice` | `am_michael` | Kokoro voice ID (see list below) |
| `speed` | `1.2` | Speech speed multiplier |
| `lang` | `en-us` | Language code |

If `voice_config.json` is missing or contains invalid JSON, all scripts fall back to the defaults shown above. You can also override only the settings you want — any omitted keys use their defaults.

Or run the interactive wizard:
```
/claude-voice:config
```

### Supported Languages

English is built-in. Other languages require installing an extra dependency:

| Language | `lang` code | Install command |
|----------|-------------|-----------------|
| English (American) | `en-us` | Built-in |
| English (British) | `en-gb` | Built-in |
| Japanese | `ja` | `uv pip install "misaki[ja]"` |
| Mandarin Chinese | `zh` | `uv pip install "misaki[zh]"` |
| Spanish | `es` | `uv pip install "misaki[es]"` |
| French | `fr` | `uv pip install "misaki[fr]"` |
| Hindi | `hi` | `uv pip install "misaki[hi]"` |
| Italian | `it` | `uv pip install "misaki[it]"` |
| Brazilian Portuguese | `pt` | `uv pip install "misaki[pt]"` |

To install all languages at once:
```bash
cd ~/.claude/plugins/cache/cris-m-claude_voice/claude-voice/0.1.0
uv pip install -e ".[all-languages]"
```

### Available Voices

Voice IDs follow the pattern: `{lang}{gender}_{name}` where the first letter is the language (`a`=American, `b`=British, `j`=Japanese, etc.) and the second is gender (`f`=Female, `m`=Male).

**English (American):**
- `af_heart`, `af_alloy`, `af_aoede`, `af_bella`, `af_jessica`, `af_kore`, `af_nicole`, `af_nova`, `af_river`, `af_sarah`, `af_sky`
- `am_adam`, `am_echo`, `am_eric`, `am_fenrir`, `am_liam`, `am_michael`, `am_onyx`, `am_puck`, `am_santa`

**English (British):**
- `bf_alice`, `bf_emma`, `bf_isabella`, `bf_lily`
- `bm_daniel`, `bm_fable`, `bm_george`, `bm_lewis`

**Japanese:**
- `jf_alpha`, `jf_gongitsune`, `jf_nezumi`, `jf_tebukuro`
- `jm_kumo`

**Mandarin Chinese:**
- `zf_xiaobei`, `zf_xiaoni`, `zf_xiaoxiao`, `zf_xiaoyi`
- `zm_yunjian`, `zm_yunxi`, `zm_yunxia`, `zm_yunyang`

**Spanish:**
- `ef_dora`, `em_alex`, `em_santa`

**French:**
- `ff_siwis`

**Hindi:**
- `hf_alpha`, `hf_beta`
- `hm_omega`, `hm_psi`

**Italian:**
- `if_sara`, `im_nicola`

**Brazilian Portuguese:**
- `pf_dora`, `pm_alex`, `pm_santa`

---

## Requirements

- Python 3.12+
- macOS (for audio output)
- Claude Code CLI
- Kokoro TTS library

---

## Uninstall

```
/plugin uninstall claude-voice@cris-m-claude_voice
```

Or run `/plugin`, go to the **Installed** tab, and uninstall from there.

---

## License

MIT License - Use freely.

---

## Resources

- [Claude Code Plugins Documentation](https://code.claude.com/docs/en/discover-plugins) - Official plugin reference
- [Official Plugin Marketplace](https://github.com/anthropics/claude-plugins-official) - Anthropic-managed plugins
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Text-to-speech engine

---

## Credits

- **Kokoro TTS** - Text-to-speech engine
- **Claude Code** - AI coding assistant by Anthropic