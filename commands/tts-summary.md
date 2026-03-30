---
description: Enable or disable spoken audio summaries of Claude responses
argument-hint: "[on|off]"
allowed-tools: [Read, Write, Edit]
---

# TTS Summary Mode

$ARGUMENTS

---

## Instructions for Claude

### Toggling

**If argument is empty or "on":** Read the current `${CLAUDE_PLUGIN_ROOT}/voice_config.json`, set `"tts_summary_enabled": true`, and write it back. Confirm to the user.

**If argument is "off":** Set `"tts_summary_enabled": false` in the config. Confirm to the user.

After toggling, remind the user that the `InstructionsLoaded` hook in `hooks.json` reads this flag and injects the TTS instruction into every conversation automatically — so it survives context compression. The user doesn't need to do anything else.

---

## The TTS_SUMMARY Format

When TTS summaries are enabled, end EVERY response with:

```
<!-- TTS_SUMMARY
Your spoken summary here.
TTS_SUMMARY -->
```

The `speak_summary.py` hook extracts text between these exact markers and speaks it aloud. Any other format will be silently ignored.

---

## Writing Good Summaries

Write **3-8 sentences** as a clear, insightful spoken briefing. The goal is to give someone a complete understanding without needing to read the screen.

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

**If using Chatterbox** (check `voice_config.json` for `"provider": "chatterbox"`):

Chatterbox renders emotion from the text itself. Write summaries with natural emotional expression — the TTS will pick up on punctuation, emphasis, and tone. For example:
- Excitement: "This is really exciting — we just hit a major milestone!"
- Concern: "Hmm, this is a bit tricky. The tests are failing because of a race condition."
- Satisfaction: "There we go, that's all fixed up nicely."

The emotion parameters (`exaggeration`, `cfg_weight`) in the config control how strongly these emotions come through.

**If using Kokoro** (default):

Kokoro is more neutral in delivery. Focus on clarity and natural pacing. The `speed` setting controls how fast the summary is spoken.

**If using MLX-Audio** (check `voice_config.json` for `"provider": "mlx"`):

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

## Quick Reference

| Command | Action |
|---------|--------|
| `/tts-summary` | Enable summaries |
| `/tts-summary on` | Enable summaries |
| `/tts-summary off` | Disable summaries |
