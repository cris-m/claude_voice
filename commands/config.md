---
description: Configure voice settings (voice, speed, language)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
---

# Voice Configuration Wizard

Interactively configure the user's voice settings and save them to `voice_config.json`.

---

## Instructions for Claude

Walk the user through choosing their voice settings step by step. After each choice, move to the next. At the end, write the config file and test it.

## Where things live

- `${CLAUDE_PLUGIN_ROOT}`: the plugin's code. It is replaced on every plugin update, so **never write to it**.
- `${CLAUDE_PLUGIN_DATA}`: persistent data that survives updates. The virtualenv is `${CLAUDE_PLUGIN_DATA}/.venv` and the user's settings are `${CLAUDE_PLUGIN_DATA}/voice_config.json`. If that config file doesn't exist yet, copy `${CLAUDE_PLUGIN_ROOT}/voice_config.json` there first, then read or edit the copy.

**First, read the current config** from `${CLAUDE_PLUGIN_DATA}/voice_config.json` to show what is currently set.

---

### Step 1: Ask about provider

Check which provider is currently configured. Ask if they want to change it.

- **Kokoro** — Lightweight, fast, 54 built-in voices, 8 languages. Good for quick notifications.
- **Chatterbox** — Higher quality, emotion control (exaggeration, cfg_weight), voice cloning from audio. Best for expressive speech.
- **MLX-Audio** (macOS Apple Silicon only) — Qwen3-TTS, emotion via text instructions, fastest on M-series chips. Best for natural assistant voice.

If they switch providers, tell them to re-run `/voice-summaries:init` to install the correct dependencies.

---

### Step 2: Language (Kokoro only)

Only ask this if provider is `kokoro`. Chatterbox and MLX auto-detect language.

**Supported Kokoro languages:**

| Code | Language | Voices | Needs dependency |
|------|----------|--------|------------------|
| `en-us` | English (American) | 20 | No |
| `en-gb` | English (British) | 8 | No |
| `ja` | Japanese | 5 | Yes |
| `zh` | Mandarin Chinese | 8 | Yes |
| `es` | Spanish | 3 | Yes |
| `fr` | French | 1 | Yes |
| `hi` | Hindi | 4 | Yes |
| `it` | Italian | 2 | Yes |
| `pt` | Brazilian Portuguese | 3 | Yes |

Use the simple config codes above in voice_config.json — they are mapped to espeak codes at runtime.

If non-English, install dependencies:

| Language | Install command |
|----------|-----------------|
| Japanese | `uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" "misaki[ja]" && uv run --no-project --python "${CLAUDE_PLUGIN_DATA}/.venv" python -m unidic download` |
| Chinese | `uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" "misaki[zh]"` |
| Korean | `uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" "misaki[ko]"` |
| Others | `uv pip install --python "${CLAUDE_PLUGIN_DATA}/.venv" misaki` |

Also ensure `espeak-ng` is installed: `brew list espeak-ng 2>/dev/null || brew install espeak-ng`

---

### Step 3: Voice (Kokoro only)

Present ONLY voices matching the chosen language. Show at most 4 options in the question tool.

#### English (American) — `en-us`
| Voice ID | Name | Gender |
|----------|------|--------|
| `af_heart` | Heart | Female |
| `af_alloy` | Alloy | Female |
| `af_bella` | Bella | Female |
| `af_jessica` | Jessica | Female |
| `af_nicole` | Nicole | Female |
| `af_nova` | Nova | Female |
| `af_river` | River | Female |
| `af_sarah` | Sarah | Female |
| `am_adam` | Adam | Male |
| `am_echo` | Echo | Male |
| `am_eric` | Eric | Male |
| `am_liam` | Liam | Male |
| `am_michael` | Michael | Male |
| `am_onyx` | Onyx | Male |
| `am_puck` | Puck | Male |

#### English (British) — `en-gb`
`bf_alice` (F), `bf_emma` (F), `bf_isabella` (F), `bf_lily` (F), `bm_daniel` (M), `bm_fable` (M), `bm_george` (M), `bm_lewis` (M)

#### Japanese — `ja`
`jf_alpha` (F), `jf_gongitsune` (F), `jf_nezumi` (F), `jf_tebukuro` (F), `jm_kumo` (M)

#### Mandarin Chinese — `zh`
`zf_xiaobei` (F), `zf_xiaoni` (F), `zf_xiaoxiao` (F), `zf_xiaoyi` (F), `zm_yunjian` (M), `zm_yunxi` (M), `zm_yunxia` (M), `zm_yunyang` (M)

#### Spanish — `es`
`ef_dora` (F), `em_alex` (M), `em_santa` (M)

#### French — `fr`
`ff_siwis` (F) — only voice available

#### Hindi — `hi`
`hf_alpha` (F), `hf_beta` (F), `hm_omega` (M), `hm_psi` (M)

#### Italian — `it`
`if_sara` (F), `im_nicola` (M)

#### Brazilian Portuguese — `pt`
`pf_dora` (F), `pm_alex` (M), `pm_santa` (M)

---

### Step 4: Speed (Kokoro only)

| Speed | Description |
|-------|-------------|
| 0.8 | Slow — easier to follow |
| 1.0 | Normal pace |
| 1.2 | Slightly fast (default) |
| 1.5 | Fast |

---

### Step 5: Chatterbox settings (Chatterbox only)

If provider is `chatterbox`, ask about:

| Setting | Range | Default | Description |
|---------|-------|---------|-------------|
| `exaggeration` | 0.0–2.0 | 0.5 | Emotion intensity. 0.25=flat, 0.5=neutral, 1.0+=dramatic |
| `cfg_weight` | 0.0–1.0 | 0.5 | Voice adherence. Lower values = more freedom |
| `temperature` | 0.0–5.0 | 0.8 | Randomness. Lower = consistent, higher = varied |

Offer presets:
- **Natural** (default): exaggeration=0.5, cfg_weight=0.5, temperature=0.8
- **Expressive**: exaggeration=0.8, cfg_weight=0.3, temperature=0.9
- **Dramatic**: exaggeration=1.5, cfg_weight=0.2, temperature=1.0
- **Custom**: let user set each value

Also ask about voice cloning:
- If they have a reference audio file (WAV, 5-10 seconds), set `audio_prompt_path` to its absolute path
- If not, leave it null to use the built-in voice

---

### Step 5b: MLX-Audio settings (MLX only)

If provider is `mlx`, ask about:

| Setting | Default | Description |
|---------|---------|-------------|
| `voice` | `Ryan` | Speaker name: `Ryan` (clear male), `Aiden` (expressive male) |
| `language` | `en` | Language code |
| `instruct` | `warm, friendly assistant` | Style/emotion instruction — any natural description works |

Offer presets:
- **Warm** (default): instruct="warm"
- **Professional**: instruct="calm, clear, professional"
- **Energetic**: instruct="enthusiastic and energetic"
- **Custom**: let user type any description

---

### Step 5c: Summary length

Ask for the default `summary_length`: `short` (1-2 sentences), `medium` (3-6 sentences, default), `long` (2-4 paragraphs) or `podcast` (4-8 minute segment). It's used by `/voice-summaries:speak` when no length is given, and by always-on summaries.

---

### Step 6: Streaming

Ask whether to stream audio (`"streaming": true`, the default). With streaming on, playback starts while the rest of the speech is still being generated, which noticeably cuts the delay on long summaries. Kokoro and MLX-Audio support it; Chatterbox ignores the setting and always generates the full clip first. For MLX, `mlx.streaming_interval` (seconds of audio per chunk, default `1.0`) trades latency against smoothness.

---

### Step 6b: Follow-up voice messages

These are spoken by hooks without Claude's involvement. Show the current `follow_ups` block and ask which to keep:

| Key | When it fires | Settings |
|-----|---------------|----------|
| `command_done` | After a Bash command that ran longer than the threshold | `enabled`, `threshold_seconds` (default 30), `message` |
| `idle_done` | When you have not interacted for the threshold after Claude finishes, and no summary was spoken | `enabled`, `threshold_seconds` (default 60, max 170), `message` |
| `notification` | When Claude Code raises a notification (permission prompt, waiting for input) | `enabled` |

Use a multi-select question to choose which are enabled, then offer to change thresholds and messages.

---

### Step 7: Write the config

Save to `${CLAUDE_PLUGIN_DATA}/voice_config.json`. Set language-appropriate `follow_ups.*.message` values using the table below if provider is Kokoro:

| Lang | command_done | idle_done |
|------|-------------|-----------|
| en-us | Done! Ready when you are. | Hey, I'm all done over here. Let me know if you need anything else. |
| en-gb | All done! Ready when you are. | I've finished up here. Let me know if you need anything else. |
| fr | Terminé! Je suis prêt quand vous l'êtes. | J'ai terminé. N'hésitez pas si vous avez besoin d'autre chose. |
| es | ¡Listo! Cuando quieras. | Ya terminé. Avísame si necesitas algo más. |
| ja | 完了しました。準備ができたらお知らせください。 | 作業が終わりました。他に何かあればお知らせください。 |
| zh | 完成了！准备好了随时告诉我。 | 我这边完成了。如果还需要什么，请告诉我。 |
| hi | हो गया! जब आप तैयार हों बताइए। | मैंने अपना काम पूरा कर लिया। अगर कुछ और चाहिए तो बताइए। |
| it | Fatto! Pronto quando vuoi. | Ho finito qui. Fammi sapere se hai bisogno di altro. |
| pt | Pronto! Quando quiser. | Terminei por aqui. Me avise se precisar de mais alguma coisa. |

---

### Step 8: Test the voice

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py "<test_sentence>"
```

Use a natural test sentence appropriate to the language.

---

## Tone

Be conversational and brief. Use the question tool to present choices one step at a time.
