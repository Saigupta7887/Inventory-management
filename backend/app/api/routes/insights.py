from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interaction import Interaction
from app.models.person import Person
from app.models.user import User
from app.services.reminders import days_since_last_contact, is_overdue

router = APIRouter(prefix="/api/insights", tags=["insights"])


def _health_score(people: list[Person]) -> int:
    """A 0-100 relationship health score (Phase 8)."""
    if not people:
        return 100
    overdue = sum(1 for p in people if is_overdue(p))
    ratio_ok = 1 - (overdue / len(people))
    return round(ratio_ok * 100)


@router.get("")
def insights(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> dict:
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))
    person_ids = [p.id for p in people]

    by_type = Counter(p.relationship_type or "uncategorized" for p in people)

    interactions: list[Interaction] = []
    if person_ids:
        interactions = list(
            db.scalars(
                select(Interaction).where(Interaction.person_id.in_(person_ids))
            )
        )

    id_to_name = {p.id: p.name for p in people}
    interactions_per_person = Counter(i.person_id for i in interactions)
    most_active = [
        {"name": id_to_name.get(pid, "?"), "count": count}
        for pid, count in interactions_per_person.most_common(5)
    ]

    neglected = sorted(
        (
            {"name": p.name, "days_since": days_since_last_contact(p)}
            for p in people
            if is_overdue(p)
        ),
        key=lambda x: (x["days_since"] is None, -(x["days_since"] or 0)),
    )[:5]

    return {
        "health_score": _health_score(people),
        "people_by_type": dict(by_type),
        "most_active": most_active,
        "neglected": neglected,
        "total_interactions": len(interactions),
    }
