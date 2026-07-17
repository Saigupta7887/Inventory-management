from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interaction import Interaction
from app.models.person import Person
from app.models.user import User
from app.schemas.interaction import InteractionOut
from app.services.reminders import (
    days_until_birthday,
    is_overdue,
    reconnect_message,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    """Dashboard aggregation (Phase 7)."""
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))

    needs_attention = [
        {
            "person_id": p.id,
            "name": p.name,
            "message": reconnect_message(p),
            "priority": p.priority,
        }
        for p in people
        if is_overdue(p)
    ]

    upcoming_events = [
        {
            "person_id": p.id,
            "name": p.name,
            "days_until": days_until_birthday(p),
            "type": "birthday",
        }
        for p in people
        if (d := days_until_birthday(p)) is not None and d <= 30
    ]
    upcoming_events.sort(key=lambda e: e["days_until"])

    person_ids = [p.id for p in people]
    recent: list[Interaction] = []
    if person_ids:
        recent = list(
            db.scalars(
                select(Interaction)
                .where(Interaction.person_id.in_(person_ids))
                .order_by(Interaction.occurred_at.desc())
                .limit(10)
            )
        )

    return {
        "total_people": len(people),
        "needs_attention": needs_attention,
        "upcoming_events": upcoming_events,
        "recent_activity": [
            InteractionOut.model_validate(i).model_dump() for i in recent
        ],
        "summary": {
            "needs_attention_count": len(needs_attention),
            "upcoming_events_count": len(upcoming_events),
        },
    }
