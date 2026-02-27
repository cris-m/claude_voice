---
description: Configure voice settings (voice, speed, language)
allowed-tools: [Bash, Read, Write, Edit]
---

# Voice Configuration Wizard

Interactively configure the user's voice settings and save them to `voice_config.json`.

---

## Instructions for Claude

Walk the user through choosing their voice settings step by step. After each choice, move to the next. At the end, write the config file and test it.

### Step 1: Ask about language

Ask the user which language they want FIRST — this determines which voices are available.

**Supported languages:**

| Config code | Language | Voices | Needs dependency |
|-------------|----------|--------|------------------|
| `en-us` | English (American) | 20 | No |
| `en-gb` | English (British) | 8 | No |
| `ja` | Japanese | 5 | Yes |
| `zh` | Mandarin Chinese | 8 | Yes |
| `es` | Spanish | 3 | Yes |
| `fr` | French | 1 | Yes |
| `hi` | Hindi | 4 | Yes |
| `it` | Italian | 2 | Yes |
| `pt` | Brazilian Portuguese | 3 | Yes |

Default is `en-us`. Use the simple config codes above in voice_config.json — they are automatically mapped to the correct espeak codes at runtime (e.g. `fr` → `fr-fr`, `zh` → `cmn`, `pt` → `pt-br`).

**Note on quality:** Japanese pronunciation in Kokoro-ONNX has known quality issues. Warn the user if they pick Japanese.

### Step 2: Install dependencies (if non-English)

**IMMEDIATELY after the user picks a language**, if it is NOT `en-us` or `en-gb`, check if the dependency is installed and install it if needed. Do this BEFORE asking about voice or speed.

**Dependency check and install:**

```bash
cd "${CLAUDE_PLUGIN_ROOT}" && .venv/bin/python -c "import misaki" 2>&1
```

If misaki is not installed, or the language-specific extra is needed:

| Language | Install command |
|----------|-----------------|
| Japanese | `cd "${CLAUDE_PLUGIN_ROOT}" && uv pip install "misaki[ja]" && .venv/bin/python -m unidic download` |
| Chinese | `cd "${CLAUDE_PLUGIN_ROOT}" && uv pip install "misaki[zh]"` |
| Korean | `cd "${CLAUDE_PLUGIN_ROOT}" && uv pip install "misaki[ko]"` |
| Spanish, French, Hindi, Italian, Portuguese | `cd "${CLAUDE_PLUGIN_ROOT}" && uv pip install misaki` |

Only Japanese, Chinese, and Korean have language-specific misaki extras. All other non-English languages just need the base `misaki` package + system `espeak-ng`.
Japanese additionally needs the unidic dictionary downloaded (500MB).

Also check that `espeak-ng` is installed on the system (required for all non-English languages):

```bash
brew list espeak-ng 2>/dev/null || brew install espeak-ng
```

Tell the user what you are installing and why. Do NOT ask for permission — just do it, since it's required for their language choice to work.

### Step 3: Ask about voice

Present ONLY the voices that match the chosen language. Use the question tool.

**All available voices by language:**

#### English (American) — `en-us`
| Voice ID | Name | Gender |
|----------|------|--------|
| `af_heart` | Heart | Female |
| `af_alloy` | Alloy | Female |
| `af_aoede` | Aoede | Female |
| `af_bella` | Bella | Female |
| `af_jessica` | Jessica | Female |
| `af_kore` | Kore | Female |
| `af_nicole` | Nicole | Female |
| `af_nova` | Nova | Female |
| `af_river` | River | Female |
| `af_sarah` | Sarah | Female |
| `af_sky` | Sky | Female |
| `am_adam` | Adam | Male |
| `am_echo` | Echo | Male |
| `am_eric` | Eric | Male |
| `am_fenrir` | Fenrir | Male |
| `am_liam` | Liam | Male |
| `am_michael` | Michael | Male |
| `am_onyx` | Onyx | Male |
| `am_puck` | Puck | Male |
| `am_santa` | Santa | Male |

#### English (British) — `en-gb`
| Voice ID | Name | Gender |
|----------|------|--------|
| `bf_alice` | Alice | Female |
| `bf_emma` | Emma | Female |
| `bf_isabella` | Isabella | Female |
| `bf_lily` | Lily | Female |
| `bm_daniel` | Daniel | Male |
| `bm_fable` | Fable | Male |
| `bm_george` | George | Male |
| `bm_lewis` | Lewis | Male |

#### Japanese — `ja`
| Voice ID | Name | Gender |
|----------|------|--------|
| `jf_alpha` | Alpha | Female |
| `jf_gongitsune` | Gongitsune | Female |
| `jf_nezumi` | Nezumi | Female |
| `jf_tebukuro` | Tebukuro | Female |
| `jm_kumo` | Kumo | Male |

#### Mandarin Chinese — `zh`
| Voice ID | Name | Gender |
|----------|------|--------|
| `zf_xiaobei` | Xiaobei | Female |
| `zf_xiaoni` | Xiaoni | Female |
| `zf_xiaoxiao` | Xiaoxiao | Female |
| `zf_xiaoyi` | Xiaoyi | Female |
| `zm_yunjian` | Yunjian | Male |
| `zm_yunxi` | Yunxi | Male |
| `zm_yunxia` | Yunxia | Male |
| `zm_yunyang` | Yunyang | Male |

#### Spanish — `es`
| Voice ID | Name | Gender |
|----------|------|--------|
| `ef_dora` | Dora | Female |
| `em_alex` | Alex | Male |
| `em_santa` | Santa | Male |

#### French — `fr`
| Voice ID | Name | Gender |
|----------|------|--------|
| `ff_siwis` | Siwis | Female |

#### Hindi — `hi`
| Voice ID | Name | Gender |
|----------|------|--------|
| `hf_alpha` | Alpha | Female |
| `hf_beta` | Beta | Female |
| `hm_omega` | Omega | Male |
| `hm_psi` | Psi | Male |

#### Italian — `it`
| Voice ID | Name | Gender |
|----------|------|--------|
| `if_sara` | Sara | Female |
| `im_nicola` | Nicola | Male |

#### Brazilian Portuguese — `pt`
| Voice ID | Name | Gender |
|----------|------|--------|
| `pf_dora` | Dora | Female |
| `pm_alex` | Alex | Male |
| `pm_santa` | Santa | Male |

Default voice is `am_michael` for English, or the first voice in the list for other languages.

When presenting choices, show at most 4 options in the question tool. If there are more voices, pick the best 3 and include an "Other" option so the user can type a voice ID.

### Step 4: Ask about speed

Ask the user how fast they want the speech. Offer these choices:

| Speed | Description |
|-------|-------------|
| 0.8 | Slow — easier to follow |
| 1.0 | Normal pace |
| 1.2 | Slightly fast (default) |
| 1.5 | Fast |

Default is `1.2`.

### Step 5: Write the config

Save the selections to `${CLAUDE_PLUGIN_ROOT}/voice_config.json`. Use the **simple config code** for lang (e.g. `fr`, `zh`, `pt`) — the code in `voice/__init__.py` auto-maps these to espeak codes at runtime.

```json
{
  "voice": "<chosen_voice>",
  "speed": <chosen_speed>,
  "lang": "<chosen_lang>"
}
```

Use the Write tool to create or overwrite the file.

### Step 6: Test the voice

Run a test so the user can hear their selection. Use a test sentence in the chosen language:

| Language | Test sentence |
|----------|---------------|
| `en-us` | "Voice configured. This is how I will sound from now on." |
| `en-gb` | "Voice configured. This is how I shall sound from now on." |
| `ja` | "音声が設定されました。これからはこの声でお話しします。" |
| `zh` | "语音已配置完成。从现在开始我会用这个声音说话。" |
| `es` | "Voz configurada. Así es como sonaré a partir de ahora." |
| `fr` | "Voix configurée. Voici comment je parlerai désormais." |
| `hi` | "आवाज़ कॉन्फ़िगर हो गई। अब से मैं ऐसे बोलूँगा।" |
| `it` | "Voce configurata. Ecco come parlerò da ora in poi." |
| `pt` | "Voz configurada. É assim que vou falar a partir de agora." |

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/speak.py" "<test_sentence>"
```

If the test fails, check error output. Common fixes:
- Missing `.venv`: run `/claude-voice:init`
- espeak not found: `brew install espeak-ng`
- Language not supported by espeak: verify the lang code mapping in `voice/__init__.py`

---

## Tone

Be conversational and brief. Don't dump all options at once in a wall of text — use the question tool to present choices naturally one step at a time.
