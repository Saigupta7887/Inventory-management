from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.models.reminder_state import ReminderState
from app.models.user import User
from app.services.reminders import (
    _as_aware,
    days_since_last_contact,
    days_until_birthday,
    is_overdue,
    reconnect_message,
    upcoming_birthday_message,
)

router = APIRouter(prefix="/api/reminders", tags=["reminders"])

_PRIORITY_RANK = {"very_high": 0, "high": 1, "medium": 2, "low": 3}


def _candidates(user: User, db: Session) -> list[dict]:
    """Compute the live reminders across the user's people."""
    people = list(db.scalars(select(Person).where(Person.owner_id == user.id)))
    out: list[dict] = []
    for person in people:
        if is_overdue(person):
            out.append(
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
            out.append(
                {
                    "person_id": person.id,
                    "person_name": person.name,
                    "kind": "birthday",
                    "message": upcoming_birthday_message(person, bday_in),
                    "priority": person.priority,
                    "days_until": bday_in,
                }
            )
    out.sort(key=lambda r: _PRIORITY_RANK.get(r["priority"], 2))
    return out


def _states(user: User, db: Session) -> dict[tuple[int, str], ReminderState]:
    rows = db.scalars(
        select(ReminderState).where(ReminderState.owner_id == user.id)
    )
    return {(s.person_id, s.kind): s for s in rows}


@router.get("")
def list_reminders(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    """Upcoming reminders — excludes snoozed (until due) and completed ones."""
    now = datetime.now(timezone.utc)
    states = _states(user, db)
    out = []
    for r in _candidates(user, db):
        st = states.get((r["person_id"], r["kind"]))
        if st:
            if st.status == "completed":
                continue
            snoozed_until = _as_aware(st.snoozed_until)
            if st.status == "snoozed" and snoozed_until and snoozed_until > now:
                continue
        out.append(r)
    return out


@router.get("/snoozed")
def snoozed_reminders(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    now = datetime.now(timezone.utc)
    states = _states(user, db)
    out = []
    for r in _candidates(user, db):
        st = states.get((r["person_id"], r["kind"]))
        snoozed_until = _as_aware(st.snoozed_until) if st else None
        if st and st.status == "snoozed" and snoozed_until and snoozed_until > now:
            out.append({**r, "snoozed_until": snoozed_until})
    return out


@router.get("/completed")
def completed_reminders(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[dict]:
    """Recently completed reminders (last 30 days), newest first."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    rows = db.scalars(
        select(ReminderState)
        .where(
            ReminderState.owner_id == user.id,
            ReminderState.status == "completed",
        )
        .order_by(ReminderState.completed_at.desc())
    )
    out = []
    for st in rows:
        completed_at = _as_aware(st.completed_at)
        if completed_at and completed_at < cutoff:
            continue
        person = db.get(Person, st.person_id)
        if not person:
            continue
        label = "Birthday wishes sent" if st.kind == "birthday" else "Reconnected"
        out.append(
            {
                "person_id": person.id,
                "person_name": person.name,
                "kind": st.kind,
                "message": f"{label} · {person.name}",
                "priority": person.priority,
                "completed_at": st.completed_at,
            }
        )
    return out


class ReminderAction(BaseModel):
    person_id: int
    kind: str  # reconnect | birthday
    days: int = 3  # for snooze


def _get_or_create_state(
    user: User, person_id: int, kind: str, db: Session
) -> ReminderState:
    person = db.get(Person, person_id)
    if person is None or person.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Person not found")
    st = db.scalar(
        select(ReminderState).where(
            ReminderState.owner_id == user.id,
            ReminderState.person_id == person_id,
            ReminderState.kind == kind,
        )
    )
    if st is None:
        st = ReminderState(owner_id=user.id, person_id=person_id, kind=kind)
        db.add(st)
    return st


@router.post("/snooze")
def snooze(
    payload: ReminderAction,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    st = _get_or_create_state(user, payload.person_id, payload.kind, db)
    st.status = "snoozed"
    st.snoozed_until = datetime.now(timezone.utc) + timedelta(days=max(1, payload.days))
    st.completed_at = None
    st.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "snoozed", "snoozed_until": st.snoozed_until.isoformat()}


@router.post("/complete")
def complete(
    payload: ReminderAction,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    st = _get_or_create_state(user, payload.person_id, payload.kind, db)
    st.status = "completed"
    st.completed_at = datetime.now(timezone.utc)
    st.snoozed_until = None
    st.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "completed"}
