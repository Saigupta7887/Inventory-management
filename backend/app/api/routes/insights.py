from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interaction import Interaction
from app.models.note import Note
from app.models.person import Person
from app.models.user import User
from app.services.reminders import _as_aware, days_since_last_contact, is_overdue

router = APIRouter(prefix="/api/insights", tags=["insights"])


def _status(person: Person) -> str:
    """healthy | needs_attention | overdue for one person."""
    days = days_since_last_contact(person)
    interval = person.reminder_interval_days or 30
    if days is None:
        return "overdue" if is_overdue(person) else "healthy"
    if days >= interval * 2:
        return "overdue"
    if days >= interval:
        return "needs_attention"
    return "healthy"


@router.get("")
def insights(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))
    person_ids = [p.id for p in people]

    # Health breakdown
    statuses = Counter(_status(p) for p in people)
    total = len(people) or 1
    healthy = statuses.get("healthy", 0)
    breakdown = {
        "healthy": round(healthy / total * 100),
        "needs_attention": round(statuses.get("needs_attention", 0) / total * 100),
        "overdue": round(statuses.get("overdue", 0) / total * 100),
    }

    interactions: list[Interaction] = []
    notes: list[Note] = []
    if person_ids:
        interactions = list(
            db.scalars(select(Interaction).where(Interaction.person_id.in_(person_ids)))
        )
        notes = list(db.scalars(select(Note).where(Note.person_id.in_(person_ids))))

    # This-week tiles
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_interactions = [
        i for i in interactions if (_as_aware(i.occurred_at) or week_ago) >= week_ago
    ]
    people_contacted = len({i.person_id for i in recent_interactions})
    followups = sum(1 for i in recent_interactions if i.follow_up)
    notes_added = sum(
        1 for n in notes if (_as_aware(n.created_at) or week_ago) >= week_ago
    )

    by_type = Counter(p.relationship_type or "uncategorized" for p in people)
    id_to_name = {p.id: p.name for p in people}
    per_person = Counter(i.person_id for i in interactions)
    most_active = [
        {"name": id_to_name.get(pid, "?"), "count": c}
        for pid, c in per_person.most_common(5)
    ]

    needs_attention = [
        {
            "person_id": p.id,
            "name": p.name,
            "days_since": days_since_last_contact(p),
            "priority": p.priority,
        }
        for p in people
        if _status(p) in ("needs_attention", "overdue")
    ]
    needs_attention.sort(
        key=lambda x: (x["days_since"] is None, -(x["days_since"] or 0))
    )

    return {
        "health_score": breakdown["healthy"],
        "health_breakdown": breakdown,
        "week": {
            "people_contacted": people_contacted,
            "followups_completed": followups,
            "notes_added": notes_added,
        },
        "people_by_type": dict(by_type),
        "most_active": most_active,
        "needs_attention": needs_attention[:5],
        "total_interactions": len(interactions),
    }
