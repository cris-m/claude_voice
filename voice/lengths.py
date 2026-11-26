"""Spoken summary lengths, shared by the always-on hook and the speak skill."""

LENGTHS = {
    "short": "1-2 sentences, about 10-15 seconds spoken. Just the outcome and the single most important thing to know.",
    "medium": "3-6 sentences, about 30-45 seconds spoken. What happened, why, the result, and what's next.",
    "long": "2-4 short paragraphs, about 1.5-3 minutes spoken. A full briefing: context, what was done and why, trade-offs, open issues, next steps.",
    "podcast": "A 4-8 minute single-host audio segment (roughly 600-1200 words). Open with a hook, walk through the story in order with transitions, explain the reasoning and interesting details, use analogies, and close with key takeaways and what to do next. Written to be listened to, not read.",
}

DEFAULT_LENGTH = "medium"


def resolve_length(name) -> str:
    name = (name or "").strip().lower()
    return name if name in LENGTHS else DEFAULT_LENGTH
