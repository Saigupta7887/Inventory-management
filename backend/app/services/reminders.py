"""Reminder intelligence (Phase 5) — computes who needs attention."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.models.interaction import Interaction
from app.models.person import Person


def _as_aware(value: datetime | None) -> datetime | None:
    """Coerce a possibly-naive datetime to UTC-aware.

    Postgres (DateTime(timezone=True)) returns aware datetimes; SQLite returns
    naive ones. Normalizing here keeps the math correct on both.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def days_since_last_contact(person: Person) -> int | None:
    last = _as_aware(person.last_interaction_at)
    if last is None:
        return None
    now = datetime.now(timezone.utc)
    delta = now - last
    return delta.days


def is_overdue(person: Person) -> bool:
    """True when it's been longer than the reminder interval since contact."""
    days = days_since_last_contact(person)
    if days is None:
        # Never contacted -> overdue once older than the interval since creation.
        created = _as_aware(person.created_at)
        if created is None:
            return False
        return (datetime.now(timezone.utc) - created).days >= person.reminder_interval_days
    return days >= person.reminder_interval_days


def days_until_birthday(person: Person, today: date | None = None) -> int | None:
    if person.birthday is None:
        return None
    today = today or datetime.now(timezone.utc).date()
    try:
        next_bday = person.birthday.replace(year=today.year)
    except ValueError:  # Feb 29
        next_bday = person.birthday.replace(year=today.year, day=28)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    return (next_bday - today).days


def reconnect_message(person: Person) -> str:
    name = person.nickname or person.name.split()[0]
    days = days_since_last_contact(person)
    if days is None:
        return f"You haven't logged any contact with {name} yet."
    return f"You haven't spoken to {name} in {days} days."


def upcoming_birthday_message(person: Person, days: int) -> str:
    name = person.nickname or person.name.split()[0]
    if days == 0:
        return f"{name}'s birthday is today!"
    if days == 1:
        return f"{name}'s birthday is tomorrow."
    return f"{name}'s birthday is in {days} days."
