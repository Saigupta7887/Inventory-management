"""Lightweight, dependency-free AI helpers.

These are intentionally simple heuristics so the app is fully functional
without an API key. Swap the bodies for a real LLM call (e.g. the Anthropic
Claude API) when you're ready — the signatures are the contract the rest of
the app depends on.
"""

from __future__ import annotations

from app.models.interaction import Interaction
from app.models.person import Person

_PREFERENCE_HINTS = ("love", "loves", "likes", "favorite", "prefers", "allergic")
_WORK_HINTS = ("job", "role", "work", "promotion", "interview", "startup", "career")
_FOLLOW_UP_HINTS = ("preparing", "planning", "upcoming", "next week", "soon", "will")


def categorize_note(content: str) -> str:
    """Classify a free-text note (Phase 3 AI categorization).

    Returns one of: preference | work_update | follow_up | fact.
    """
    text = content.lower()
    if any(h in text for h in _PREFERENCE_HINTS):
        return "preference"
    if any(h in text for h in _WORK_HINTS):
        return "work_update"
    if any(h in text for h in _FOLLOW_UP_HINTS):
        return "follow_up"
    return "fact"


def suggested_question(person: Person, last: Interaction | None) -> str:
    """A suggested opener for the context card (Phase 6)."""
    name = person.nickname or person.name.split()[0]
    if last and last.follow_up:
        return f"Ask {name}: {last.follow_up}"
    if last and last.summary:
        return f"Follow up with {name} about \"{last.summary}\"."
    return f"Ask {name} how they've been lately."


def draft_message(person: Person, last: Interaction | None) -> str:
    """An AI-style message draft (Phase 6)."""
    name = person.nickname or person.name.split()[0]
    if last and last.summary:
        return f"Hey {name}, been thinking about our chat on {last.summary}. How's it going?"
    return f"Hey {name}! It's been a little while — how have you been?"
