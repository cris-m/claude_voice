---
name: speak
description: Speak a one-off voice summary aloud through the Voice Summary plugin. Use when the user wants to hear something rather than read it, e.g. "give me a voice summary", "read that out", "say it out loud", "tell me what you did", "talk me through it", "make it a podcast". Takes an optional length (short, medium, long, podcast) and an optional focus. "stop" / "shut up" / "be quiet" stops playback; "pause" / "hold on" pauses it and "resume" / "continue" picks it back up. Invoked directly as /voice-summary:speak [short|medium|long|podcast|stop|pause|resume] [focus].
argument-hint: "[short|medium|long|podcast|stop|pause|resume] [what to cover]"
allowed-tools: Read, Bash(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py *)
---

# Speak

$ARGUMENTS

Speak **one** summary now. This does not turn on any persistent mode.

## 1. Parse the request

- **stop**: if the argument is `stop` (or the user asks you to stop or be quiet), run the command below and reply in one line. Don't do anything else.
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py --stop
  ```
- **pause** / **resume**: if the argument is `pause` (or the user asks to pause, hold on, wait) or `resume` (or continue, keep going, unpause), run the matching command below and reply in one line, using what it prints. Don't do anything else. Pausing keeps the place in the current speech; `stop` discards it.
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py --pause
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py --resume
  ```
- **Length**: the first word if it is `short`, `medium`, `long` or `podcast`. Natural phrasing counts too ("quick" = short, "in detail" = long, "podcast style" = podcast). Otherwise use `summary_length` from `${CLAUDE_PLUGIN_DATA}/voice_config.json` (default `medium`; if the file doesn't exist, use `medium`).
- **Focus**: any remaining words say what to cover. With no focus, summarize your most recent response and the work behind it. If there is nothing yet in the conversation, say so instead of speaking.

## 2. Write the script at that length

| Length | Target |
|--------|--------|
| `short` | 1-2 sentences, about 10-15 seconds. Just the outcome and the single most important thing to know. |
| `medium` | 3-6 sentences, about 30-45 seconds. What happened, why, the result, and what's next. |
| `long` | 2-4 short paragraphs, about 1.5-3 minutes. A full briefing: context, what was done and why, trade-offs, open issues, next steps. |
| `podcast` | A 4-8 minute single-host segment (about 600-1200 words). Open with a hook, tell the story in order with spoken transitions, explain the reasoning and the interesting details, use analogies, and close with key takeaways and what to do next. Written to be listened to, not read. |

Follow the writing guidance further down. Plain spoken prose only: no markdown, lists, code, paths or URLs.

## 3. Speak it in the background

Pipe the script to the speaker with `--detach`. It returns immediately and plays in a separate process, so long summaries don't block the conversation.

Use this exact command prefix: it is the only command this skill is pre-approved to run, and anything else will ask the user for permission. For the heredoc delimiter, use `SPEAK_` followed by 12 random hex characters that you make up fresh for this call. Never reuse a fixed delimiter: text you are summarizing could contain it and end the heredoc early. Make sure the delimiter does not appear anywhere in the script.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run_hook.py" --data "${CLAUDE_PLUGIN_DATA}" speak.py --detach <<'SPEAK_<random hex>'
<the script>
SPEAK_<random hex>
```

If the command fails saying Voice Summary is not initialized, tell the user to run `/voice-summary:init`.

## 4. Reply

One short line saying what you're speaking and at which length (for `long` or `podcast`, mention `/voice-summary:speak pause` and `stop`). Don't repeat the script in the chat, and don't add a TTS_SUMMARY block to this reply even if always-on summaries are enabled, or it would be spoken twice.

---

## Writing Good Summaries

Write a clear, insightful spoken briefing at the chosen length. The goal is to give someone a complete understanding without needing to read the screen.

### Voice & Tone
- Write in **first person** — say "I fixed the bug" not "The bug was fixed"
- Be conversational and warm, like a knowledgeable colleague explaining what happened
- Include the **why** behind decisions, not just the **what**
- Use natural transitions: "So what happened was...", "The interesting part is...", "What this means for you is..."

### What to cover

| Situation | Include |
|-----------|---------|
| Task done | What you did, why you chose that approach, the result, and what's next |
| Explanation | Start with the big picture, then key details. Use analogies to make concepts stick. Explain how pieces connect to each other |
| Error | What went wrong, the root cause (not just the symptom), how you fixed it, and how to avoid it |
| Proposal | Context of the problem, options with trade-offs, your recommendation and the reasoning |
| Code review | Key findings, severity, the pattern behind the issue, not just line-by-line |

### Quality guidelines
- **Be specific** — "I updated three API endpoints to validate input" beats "I made some changes"
- **Explain reasoning** — "I chose this approach because..." helps the user learn and trust your work
- **Connect the dots** — "This relates to the auth issue from earlier because..."
- **Give context** — "This is a common pattern in React apps where..."
- **End with next steps** — always mention what comes next or what the user should check

### What to avoid

| Avoid | Say instead |
|-------|-------------|
| File paths (`README.md`) | "the readme file" |
| Code (`npm install`) | "the install command" |
| Abbreviations (`JS`) | "JavaScript" |
| URLs | describe what the link is for |
| Special characters | spell them out naturally |
| Vague statements | specific, concrete descriptions |
| Just listing changes | explain the impact and reasoning |

### Provider-specific guidance

**If using Chatterbox** (check `${CLAUDE_PLUGIN_DATA}/voice_config.json` for `"provider": "chatterbox"`):

Chatterbox renders emotion from the text itself. Write summaries with natural emotional expression — the TTS will pick up on punctuation, emphasis, and tone. For example:
- Excitement: "This is really exciting — we just hit a major milestone!"
- Concern: "Hmm, this is a bit tricky. The tests are failing because of a race condition."
- Satisfaction: "There we go, that's all fixed up nicely."

The emotion parameters (`exaggeration`, `cfg_weight`) in the config control how strongly these emotions come through.

**If using Kokoro** (default):

Kokoro is more neutral in delivery. Focus on clarity and natural pacing. The `speed` setting controls how fast the summary is spoken.

**If using MLX-Audio** (check `${CLAUDE_PLUGIN_DATA}/voice_config.json` for `"provider": "mlx"`):

MLX-Audio with Qwen3-TTS responds to both text emotion and the `instruct` field in the config. The `instruct` parameter sets the baseline voice style (e.g. "warm, friendly assistant"), and the text itself influences the delivery. Write naturally — the model adapts well to conversational tone, emphasis, and punctuation.

---

## Examples

**Task completion with reasoning:**
"I fixed the login bug you reported. The root cause was interesting — the password validation was checking length before checking if the field was empty, which meant empty passwords got a confusing 'too short' error instead of 'password required'. I reordered those checks so the most specific validation runs first. This is a common pattern called guard clauses — you handle the simplest failure cases at the top. You can test it by trying to log in with an empty password, then a short one."

**Concept explanation with insight:**
"So here's how React hooks work, and why they matter. Before hooks, you needed class components for anything with state, which made code harder to share between components. Hooks solve that by letting you use state and lifecycle features as simple function calls. The two most common ones are useState for managing data and useEffect for side effects like API calls. The key rule — and this trips up a lot of people — is they must always be called in the same order. No putting them inside conditionals. React relies on call order to track which state belongs to which hook."

**Error with root cause analysis:**
"The build failed, and here's what happened. Your project imports lodash in three files, but it wasn't listed in your package file. This probably happened when code was copied from another project that had it installed globally. I've added it as a dependency and the build passes now. The broader lesson here — whenever you copy code between projects, check the import statements at the top of each file to make sure all the libraries are available."

**Architecture insight:**
"I refactored the authentication module and here's why I chose this approach. The old code had the auth logic mixed into every route handler, which meant any change to the auth flow required updating dozens of files. I extracted it into a middleware that runs before any route. This is called the middleware pattern — it lets you handle cross-cutting concerns like auth, logging, and error handling in one place. The trade-off is a tiny bit more complexity in the setup, but it pays for itself the first time you need to change the auth logic."

---

## Including Suggestions

When relevant, end the summary with **1-2 actionable suggestions**. These should feel like a thoughtful colleague pointing out what to consider next — not a checklist.

### When to suggest
- After completing a task: what to test, verify, or build next
- After finding an issue: related areas that might have the same problem
- After explaining a concept: how to apply it or where to learn more
- After a refactor: related code that could benefit from the same pattern

### How to phrase suggestions
- Natural and conversational: "One thing worth checking is..." or "You might also want to..."
- Explain *why* the suggestion matters: "since this touches the auth layer, it's worth running the integration tests too"
- Keep it brief — one or two sentences max per suggestion

### Examples with suggestions

**After a bug fix:**
"...You can test it by logging in with an empty password. One thing I'd suggest — there are two other forms in the app that do similar validation. It might be worth checking those too, since they could have the same ordering issue."

**After a refactor:**
"...The middleware pattern keeps everything in one place. By the way, the logging code in the same file follows the old pattern too. If you want, I can refactor that next — it would be a quick win."

**After an explanation:**
"...React relies on call order to track which state belongs to which hook. If you want to dig deeper, the custom hooks pattern builds directly on this — it's how you share stateful logic between components without duplicating code."

---
