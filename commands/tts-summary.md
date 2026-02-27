---
description: Enable or disable spoken audio summaries of Claude responses
argument-hint: "[on|off]"
---

# TTS Summary Mode

Control spoken audio summaries of Claude's responses using Kokoro text-to-speech.

---

## Usage

```
/tts-summary        → Enable summaries (default)
/tts-summary on     → Enable summaries
/tts-summary off    → Disable summaries
```

---

## Current Request

$ARGUMENTS

---

## Instructions for Claude

**If the argument is empty or "on":**
- Enable TTS Summary mode
- Add a TTS_SUMMARY block at the end of EVERY response from now on

**If the argument is "off":**
- Disable TTS Summary mode
- STOP adding TTS_SUMMARY blocks to responses
- Respond normally without audio summaries

---

## CRITICAL: Exact Marker Format Required

You MUST use these EXACT markers. The script ONLY recognizes this specific format:

```
<!-- TTS_SUMMARY
Your detailed spoken summary here.
TTS_SUMMARY -->
```

### WRONG Formats (Will NOT Work)

| Wrong Format | Why It Fails |
|--------------|--------------|
| `Audio Summary: text` | No markers, script cannot find it |
| `**Summary:** text` | No markers, just plain text |
| `TTS Summary: text` | No markers, will not be spoken |
| `<!-- TTS: text -->` | Wrong marker name |
| `<!-- summary text -->` | Wrong marker name |

### CORRECT Format

The opening marker is: `<!-- TTS_SUMMARY`
The closing marker is: `TTS_SUMMARY -->`
Your summary text goes BETWEEN these two lines.

**Always end your response with this exact structure:**

```
<!-- TTS_SUMMARY
Your complete audio briefing goes here. Write naturally as if speaking to the user. Include all important information they need to understand what happened, what they learned, or what you recommend.
TTS_SUMMARY -->
```

---

## The Purpose of Summaries

The summary is a complete audio briefing for the user. They may be away from the screen, multitasking, or visually impaired. Your summary should give them everything important from your response.

**The summary is NOT just about what you did. It covers:**

| When You... | Your Summary Should... |
|-------------|------------------------|
| Complete a task | Explain what you did and the result |
| Explain a concept | Summarize the key points they need to understand |
| Propose solutions | Present the options and your recommendation |
| Answer a question | Give the answer with enough context |
| Find information | Share the important findings |
| Encounter a problem | Explain what went wrong and how to fix it |

---

## Summary Types

### Type 1: Task Completion

When you finish doing something for the user.

**Include:**
- What you did
- Why you did it that way
- The result
- What they can do next

**Example:**
"I fixed the login bug you reported. The problem was in the password validation where it checked length before checking if the field was empty. I reordered those checks so users now see the correct error message. You can test it by trying to log in with an empty password field."

---

### Type 2: Concept Explanation

When you explain how something works or teach the user something.

**Include:**
- The main concept in simple terms
- Why it matters
- How it connects to what they are doing
- Key points to remember

**Example:**
"Let me explain how React hooks work. Hooks are functions that let you use state and other React features without writing a class. The most common ones are useState for managing data and useEffect for handling side effects like API calls. The important rule is that hooks must always be called in the same order, so you cannot put them inside conditions or loops. This is why your code was breaking when you tried to conditionally use useState."

---

### Type 3: Solution Proposal

When you present options or recommend an approach.

**Include:**
- The options available
- Pros and cons of each
- Your recommendation
- Why you recommend it

**Example:**
"For your database needs, you have three good options. PostgreSQL is best for complex queries and data relationships. MongoDB is better if your data structure changes frequently. SQLite works well for smaller applications that run locally. I recommend PostgreSQL for your project because you mentioned needing to join data from multiple tables, and PostgreSQL handles that efficiently. It also scales well if your user base grows."

---

### Type 4: Question Answer

When you answer a question the user asked.

**Include:**
- The direct answer
- Important context
- Any caveats or exceptions
- Related information they might need

**Example:**
"Yes, you can use async await inside a useEffect hook, but not directly. The useEffect callback cannot be async itself, so you need to define an async function inside the effect and then call it. This is because React expects useEffect to return either nothing or a cleanup function, but async functions always return a promise. I can show you the pattern in the code if you want to see how it looks."

---

### Type 5: Research Findings

When you search for information or investigate something.

**Include:**
- What you found
- Where you found it
- What it means for the user
- Recommendations based on findings

**Example:**
"I researched the best open source language models available right now. DeepSeek version three point two is currently leading with ninety four percent accuracy on benchmarks and it is free to use under the MIT license. Llama four point one from Meta offers the longest context window at ten million tokens, which is great for analyzing large documents. For your chatbot project, I recommend starting with DeepSeek because it balances performance and cost well."

---

### Type 6: Problem Explanation

When something goes wrong or you encounter an error.

**Include:**
- What the problem is
- Why it happened
- How to fix it
- How to prevent it in the future

**Example:**
"The build failed because of a missing dependency. Your project needs the lodash library but it is not listed in your package file. This usually happens when code is copied from another project without copying the dependencies. To fix this, you need to install lodash by adding it to your dependencies. After that, run the install command again and the build should work. In the future, check for import statements when copying code to make sure you have all required packages."

---

## Summary Length Guidelines

| Response Type | Summary Length |
|---------------|----------------|
| Simple task | 2 to 3 sentences |
| Complex task | 3 to 4 sentences |
| Concept explanation | 4 to 6 sentences |
| Solution proposal | 4 to 6 sentences |
| Research findings | 3 to 5 sentences |
| Error or problem | 3 to 4 sentences |

**Never be too brief.** Summaries like "Done" or "Here is the answer" tell the user nothing useful.

---

## What To Avoid

| Avoid | Why |
|-------|-----|
| File paths | Sound robotic when spoken |
| Technical symbols | TTS reads them literally |
| Abbreviations | Say "JavaScript" not "JS" |
| Commands | Describe the action instead |
| URLs | Impossible to understand when spoken |
| Special characters | TTS reads them as words |
| One word answers | Not informative |
| Code snippets | Cannot be understood when heard |

---

## Transforming Technical to Natural Speech

| Technical | Natural |
|-----------|---------|
| Check the `README.md` | Check the readme file |
| Run `npm install` | Run the install command |
| The API returns 404 | The server could not find the data |
| Update the `.env` file | Update the environment configuration |
| The DB connection failed | The database connection failed |
| Fix the UI bug | Fix the user interface bug |
| The JS code | The JavaScript code |
| Use async/await | Use async await pattern |

---

## Good vs Bad Examples

### Explaining a Concept

**Bad:**
"Hooks let you use state."

**Good:**
"React hooks are functions that let you add features to your components without using classes. The useState hook stores data that can change, and the useEffect hook runs code when your component loads or updates. The key rule is that hooks must be called in the same order every time, so you cannot put them inside if statements. This pattern makes your code simpler and easier to reuse."

---

### Proposing a Solution

"I looked at the three approaches for your authentication system. Option one using sessions is simpler but requires server memory. Option two using tokens is stateless and works better for mobile apps. Option three using a third party service is easiest but costs money. I recommend option two with tokens because your app needs to work on both web and mobile, and tokens handle that well without extra server costs."

---

### Answering a Question

**Bad:**
"Yes, that is possible."

**Good:**
"Yes, you can definitely do that. The way to implement it is by using a custom hook that combines useState and useEffect. This pattern is common when you need to sync state with local storage or an external source. I included an example in my response that shows the exact structure. The important part is the cleanup function that prevents memory leaks when the component unmounts."

---

## Quick Reference

| Command | Action |
|---------|--------|
| `/tts-summary` | Enable summaries |
| `/tts-summary on` | Enable summaries |
| `/tts-summary off` | Disable summaries |

---

## Remember

Your summary is a complete audio briefing.

The user should understand:
- What happened or what they need to know
- Why it matters
- What they can do with this information

**Be informative. Be detailed. Be helpful.**

Write for someone who cannot see the screen.
