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
├── hooks/
│   └── claude_voice/           # Main package (copy to ~/.claude/hooks/)
│       ├── voice/              # TTS engine
│       │   ├── __init__.py     # Package exports
│       │   ├── voice.py        # Kokoro TTS class
│       │   └── utils.py        # Text cleaning utilities
│       │
│       ├── scripts/            # Hook scripts
│       │   ├── speak.py        # Basic speech function
│       │   ├── speak_notification.py  # Speaks notifications
│       │   ├── speak_summary.py       # Extracts and speaks summaries
│       │   └── debug_hook.py   # Logs hook data for debugging
│       │
│       ├── pyproject.toml      # Python dependencies
│       └── uv.lock             # Locked dependency versions
│
├── command/                    # Claude Code skills
│   └── tts-summary.md          # Enable/disable TTS summaries
│
├── settings.json               # Example hook configuration
├── LICENSE                     # MIT License
└── README.md                   # This file
```

---

## Installation

### Step 1: Copy Project to Claude Configuration

Claude Code stores its configuration in the `~/.claude/` folder. We will copy the Claude Voice project into this folder so everything stays organized together.

```bash
mkdir -p ~/.claude/hooks
cp -r ~/claude_voice/hooks/claude_voice ~/.claude/hooks/
```

This copies the entire project to `~/.claude/hooks/claude_voice/`

**Why copy here?**
- Keeps all Claude-related files in one place
- The `~/.claude/` folder is backed up with your Claude settings
- Paths in the hook configuration use this location

### Step 2: Install Dependencies

Navigate to the project folder and install dependencies:

```bash
cd ~/.claude/hooks/claude_voice
```

#### Option A: Using uv (Recommended - Faster)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager. The project includes a `pyproject.toml` with all dependencies:

```bash
uv sync
```

This creates the virtual environment and installs all dependencies automatically.

#### Option B: Using Python

If you do not have uv, use standard Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install kokoro sounddevice numpy
```

### Step 3: Add Hooks to Your Settings

You have two options to configure hooks:

#### Option A: Using Claude Code Interactive UI (Recommended)

Claude Code has a built-in hooks menu. Run this command in Claude Code:

```
/hooks
```

This opens an interactive menu where you can add hooks without editing JSON files.

#### Option B: Manual Configuration

**WARNING:** Do NOT copy the entire `settings.json` file. This will overwrite your existing Claude settings and you will lose your configurations.

Instead, you need to MERGE the hooks into your existing settings:

#### Option A: If You Have No Existing Hooks

If your `~/.claude/settings.json` does not have a "hooks" section, you can add one:

1. Open your settings file:
   ```bash
   nano ~/.claude/settings.json
   ```

2. Add the hooks section from `claude_voice/settings.json` into your file

3. Make sure the JSON structure is valid

#### Option B: If You Already Have Hooks

If you already have hooks configured, add the Claude Voice hooks to your existing hooks section.

#### What To Add

Open `~/.claude/hooks/claude_voice/settings.json` and copy the hooks inside the "hooks" object:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/claude_voice/.venv/bin/python ~/.claude/hooks/claude_voice/scripts/speak_notification.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/claude_voice/.venv/bin/python ~/.claude/hooks/claude_voice/scripts/speak.py 'Command finished'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/claude_voice/.venv/bin/python ~/.claude/hooks/claude_voice/scripts/speak_summary.py"
          }
        ]
      }
    ]
  }
}
```


### Step 4: Copy Skills to Claude Commands

Claude Code looks for custom commands (skills) in `~/.claude/commands/`. Copy the TTS summary skill there:

```bash
cp ~/.claude/hooks/claude_voice/command/tts-summary.md ~/.claude/commands/
```

This makes the `/tts-summary` command available in Claude Code.

### Step 5: Restart Claude Code

Close and reopen Claude Code for hooks to take effect.

---

## Usage

### Enable Spoken Summaries

```
/tts-summary
```

or

```
/tts-summary on
```

### Disable Spoken Summaries

```
/tts-summary off
```

---

## Understanding settings.json

Your Claude settings file at `~/.claude/settings.json` may contain many configurations:

```json
{
  "theme": "dark",
  "model": "opus",
  "hooks": {
    ...
  },
  "other_settings": "..."
}
```

The Claude Voice hooks go INSIDE the "hooks" section. If you already have other hooks, add these alongside them.

### Example: Merging Hooks

**Your existing settings.json:**
```json
{
  "theme": "dark",
  "hooks": {
    "PreToolUse": [...]
  }
}
```

**After adding Claude Voice:**
```json
{
  "theme": "dark",
  "hooks": {
    "PreToolUse": [...],
    "Notification": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

Notice that we ADDED to the hooks, not replaced the whole file.

---

## Hook Configuration

The hooks are configured in `settings.json`:

| Hook | Trigger | Action |
|------|---------|--------|
| Stop | Response completes | Speaks TTS_SUMMARY |
| Notification | Claude notification | Speaks message |
| PostToolUse (Bash) | Command finishes | Says "Command finished" |

### Customizing

Edit `settings.json` to:

- Change which hooks are active
- Modify script paths
- Add new hooks

---

## How Summaries Work

When `/tts-summary` is enabled, Claude adds a hidden summary block:

```
<!-- TTS_SUMMARY
Your summary text here.
TTS_SUMMARY -->
```

The `speak_summary.py` script:

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
2. Verify `settings.json` is at `~/.claude/settings.json`
3. Check virtual environment is set up correctly
4. Look at `/tmp/speak_summary_error.log`

### Summary Not Spoken

1. Run `/tts-summary` to enable
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
  ~/.claude/hooks/claude_voice/.venv/bin/python \
  ~/.claude/hooks/claude_voice/scripts/speak_summary.py
```

---

## Voice Configuration
The default voice settings in `speak.py`:
| Setting | Value |
|---------|-------|
| Voice | af_sarah |
| Speed | 1.2 |
| Language | en-us |

### Available Voices
**Male Voices:**
- `am_michael` - Michael (American English)
- `bm_george` - George (British English)
- `am_adam` - Adam (Mandarin Chinese)

**Female Voices:**
- `af_sky` - Sky (Spanish)
- `af_nicole` - Nicole (French)
- `af_sarah` - Sarah (Hindi)
- `bf_emma` - Emma (Italian)
- `af_bella` - Bella (Japanese)
- `bf_isabella` - Isabella (Portuguese)

To change voices, edit the `speak()` calls in the script files with the voice ID:
```python
self.speak("Your text here", voice="am_michael", lang="en-us")
```

---

## Requirements

- Python 3.10+
- macOS (for audio output)
- Claude Code CLI
- Kokoro TTS library

---

## Files to Set Up

To set up on a new machine:

| Step | Action |
|------|--------|
| 1. Move project | Copy `claude_voice` folder to `~/.claude/hooks/` |
| 2. Settings | **MERGE** hooks into `~/.claude/settings.json` (do not overwrite) |
| 3. Skills | Copy `command/tts-summary.md` to `~/.claude/commands/` |

**Remember:**
- Do NOT use `cp` for settings.json - it will delete your existing settings
- The scripts stay in the `~/.claude/hooks/claude_voice/` folder
- All paths in hooks use `~/.claude/hooks/claude_voice/` as the base

---

## License

MIT License - Use freely.

---

## Resources

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks) - Official hooks reference
- [Claude Code Showcase](https://github.com/ChrisWiles/claude-code-showcase) - Example project configurations
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Text-to-speech engine

---

## Credits

- **Kokoro TTS** - Text-to-speech engine
- **Claude Code** - AI coding assistant by Anthropic
