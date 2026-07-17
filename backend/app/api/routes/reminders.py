from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.models.user import User
from app.services.reminders import (
    days_since_last_contact,
    days_until_birthday,
    is_overdue,
    reconnect_message,
    upcoming_birthday_message,
)

router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.get("")
def list_reminders(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    """Computed reminders across all of the user's people (Phase 5)."""
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))
    reminders: list[dict] = []

    for person in people:
        if is_overdue(person):
            reminders.append(
                {
                    "person_id": person.id,
                    "person_name": person.name,
                    "kind": "reconnect",
                    "message": reconnect_message(person),
                    "priority": person.priority,
                    "days_since": days_since_last_contact(person),
                }
            )
        bday_in = days_until_birthday(person)
        if bday_in is not None and bday_in <= 14:
            reminders.append(
                {
                    "person_id": person.id,
                    "person_name": person.name,
                    "kind": "birthday",
                    "message": upcoming_birthday_message(person, bday_in),
                    "priority": person.priority,
                    "days_until": bday_in,
                }
            )

    priority_rank = {"very_high": 0, "high": 1, "medium": 2, "low": 3}
    reminders.sort(key=lambda r: priority_rank.get(r["priority"], 2))
    return reminders
