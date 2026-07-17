"""AI helpers for notes and messages (Phases 3 & 6).

When ANTHROPIC_API_KEY is configured these call the Claude API for smarter
output; otherwise they fall back to dependency-free heuristics so the app is
fully functional with no key. Every function degrades gracefully — any API or
import error falls back to the heuristic, so a bad key never breaks the app.
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.models.interaction import Interaction
from app.models.person import Person

logger = logging.getLogger(__name__)

CATEGORIES = ("preference", "work_update", "follow_up", "fact")

_PREFERENCE_HINTS = ("love", "loves", "likes", "favorite", "prefers", "allergic")
_WORK_HINTS = ("job", "role", "work", "promotion", "interview", "startup", "career")
_FOLLOW_UP_HINTS = ("preparing", "planning", "upcoming", "next week", "soon", "will")


# ---- Claude client --------------------------------------------------------

def _ai_enabled() -> bool:
    return bool(settings.anthropic_api_key)


def _claude_text(system: str, user: str, max_tokens: int) -> str | None:
    """One-shot Claude call returning trimmed text, or None on any failure."""
    if not _ai_enabled():
        return None
    try:
        import anthropic  # lazy import so the app runs without the package

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        for block in resp.content:
            if block.type == "text":
                return block.text.strip()
        return None
    except Exception as exc:  # noqa: BLE001 — never let AI errors break the app
        logger.warning("Claude call failed, using heuristic fallback: %s", exc)
        return None


def _person_line(person: Person) -> str:
    bits = [f"Name: {person.name}"]
    if person.relationship_type:
        bits.append(f"Relationship: {person.relationship_type}")
    if person.tags:
        bits.append(f"Tags: {person.tags}")
    return "; ".join(bits)


def _last_line(last: Interaction | None) -> str:
    if not last:
        return "No interactions logged yet."
    parts = [f"Channel: {last.channel}"]
    if last.summary:
        parts.append(f"Summary: {last.summary}")
    if last.mood:
        parts.append(f"Mood: {last.mood}")
    if last.follow_up:
        parts.append(f"Follow-up: {last.follow_up}")
    return "; ".join(parts)


# ---- Public API (Claude with heuristic fallback) --------------------------

def categorize_note(content: str) -> str:
    """Classify a free-text note (Phase 3). One of CATEGORIES."""
    out = _claude_text(
        system=(
            "You label a short note about a personal contact with exactly one "
            "category from this list: preference, work_update, follow_up, fact. "
            "Reply with only the category word, nothing else."
        ),
        user=content,
        max_tokens=16,
    )
    if out:
        label = out.lower().strip().strip(".")
        if label in CATEGORIES:
            return label
    return _heuristic_category(content)


def suggested_question(person: Person, last: Interaction | None) -> str:
    """A suggested opener for the context card (Phase 6)."""
    out = _claude_text(
        system=(
            "You help someone stay close to the people in their life. Given a "
            "contact and the last interaction, suggest one short, warm, specific "
            "question they could ask to reconnect. Reply with just the question."
        ),
        user=f"{_person_line(person)}\nLast interaction: {_last_line(last)}",
        max_tokens=80,
    )
    return out or _heuristic_question(person, last)


def draft_message(person: Person, last: Interaction | None) -> str:
    """An AI message draft to send the person (Phase 6)."""
    out = _claude_text(
        system=(
            "You draft a short, friendly, natural text message (1-2 sentences) "
            "to help someone reconnect with a contact. Warm, not formal; no "
            "placeholders. Reply with just the message."
        ),
        user=f"{_person_line(person)}\nLast interaction: {_last_line(last)}",
        max_tokens=120,
    )
    return out or _heuristic_draft(person, last)


# ---- Heuristic fallbacks --------------------------------------------------

def _heuristic_category(content: str) -> str:
    text = content.lower()
    if any(h in text for h in _PREFERENCE_HINTS):
        return "preference"
    if any(h in text for h in _WORK_HINTS):
        return "work_update"
    if any(h in text for h in _FOLLOW_UP_HINTS):
        return "follow_up"
    return "fact"


def _heuristic_question(person: Person, last: Interaction | None) -> str:
    name = person.nickname or person.name.split()[0]
    if last and last.follow_up:
        return f"Ask {name}: {last.follow_up}"
    if last and last.summary:
        return f'Follow up with {name} about "{last.summary}".'
    return f"Ask {name} how they've been lately."


def _heuristic_draft(person: Person, last: Interaction | None) -> str:
    name = person.nickname or person.name.split()[0]
    if last and last.summary:
        return f"Hey {name}, been thinking about our chat on {last.summary}. How's it going?"
    return f"Hey {name}! It's been a little while — how have you been?"
