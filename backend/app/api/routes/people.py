from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interaction import Interaction
from app.models.note import Note
from app.models.person import Person
from app.models.user import User
from app.schemas.interaction import InteractionCreate, InteractionOut
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate
from app.schemas.person import PersonCreate, PersonOut, PersonUpdate
from app.services.ai import categorize_note, draft_message, suggested_question

router = APIRouter(prefix="/api/people", tags=["people"])


def _get_owned_person(person_id: int, user: User, db: Session) -> Person:
    person = db.get(Person, person_id)
    if person is None or person.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.get("", response_model=list[PersonOut])
def list_people(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Person]:
    return list(
        db.scalars(
            select(Person)
            .where(Person.owner_id == user.id)
            .order_by(Person.name)
        )
    )


@router.post("", response_model=PersonOut, status_code=status.HTTP_201_CREATED)
def create_person(
    payload: PersonCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Person:
    person = Person(owner_id=user.id, **payload.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonOut)
def get_person(
    person_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Person:
    return _get_owned_person(person_id, user, db)


@router.patch("/{person_id}", response_model=PersonOut)
def update_person(
    person_id: int,
    payload: PersonUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Person:
    person = _get_owned_person(person_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    person = _get_owned_person(person_id, user, db)
    db.delete(person)
    db.commit()


# ----- Notes (Phase 3) -----------------------------------------------------


@router.get("/{person_id}/notes", response_model=list[NoteOut])
def list_notes(
    person_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Note]:
    _get_owned_person(person_id, user, db)
    return list(
        db.scalars(
            select(Note)
            .where(Note.person_id == person_id)
            .order_by(Note.pinned.desc(), Note.created_at.desc())
        )
    )


@router.post(
    "/{person_id}/notes",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
)
def add_note(
    person_id: int,
    payload: NoteCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    _get_owned_person(person_id, user, db)
    category = payload.category or (
        categorize_note(payload.content) if user.ai_suggestions_enabled else None
    )
    note = Note(
        person_id=person_id,
        content=payload.content,
        category=category,
        pinned=payload.pinned,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/{person_id}/notes/{note_id}", response_model=NoteOut)
def update_note(
    person_id: int,
    note_id: int,
    payload: NoteUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Note:
    _get_owned_person(person_id, user, db)
    note = db.get(Note, note_id)
    if note is None or note.person_id != person_id:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete(
    "/{person_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_note(
    person_id: int,
    note_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _get_owned_person(person_id, user, db)
    note = db.get(Note, note_id)
    if note is None or note.person_id != person_id:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()


# ----- Interactions (Phase 4) ---------------------------------------------


@router.get("/{person_id}/interactions", response_model=list[InteractionOut])
def list_interactions(
    person_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Interaction]:
    _get_owned_person(person_id, user, db)
    return list(
        db.scalars(
            select(Interaction)
            .where(Interaction.person_id == person_id)
            .order_by(Interaction.occurred_at.desc())
        )
    )


@router.post(
    "/{person_id}/interactions",
    response_model=InteractionOut,
    status_code=status.HTTP_201_CREATED,
)
def log_interaction(
    person_id: int,
    payload: InteractionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Interaction:
    person = _get_owned_person(person_id, user, db)
    occurred = payload.occurred_at or datetime.now(timezone.utc)
    interaction = Interaction(
        person_id=person_id,
        channel=payload.channel,
        summary=payload.summary,
        mood=payload.mood,
        follow_up=payload.follow_up,
        occurred_at=occurred,
    )
    db.add(interaction)
    # Update last interaction date automatically (Phase 4).
    person.last_interaction_at = occurred
    db.commit()
    db.refresh(interaction)
    return interaction


# ----- AI context card (Phase 6) ------------------------------------------


@router.get("/{person_id}/context-card")
def context_card(
    person_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    person = _get_owned_person(person_id, user, db)
    pinned = list(
        db.scalars(
            select(Note).where(Note.person_id == person_id, Note.pinned.is_(True))
        )
    )
    last = db.scalar(
        select(Interaction)
        .where(Interaction.person_id == person_id)
        .order_by(Interaction.occurred_at.desc())
    )
    return {
        "person_id": person.id,
        "name": person.name,
        "last_interaction": last.occurred_at if last else None,
        "pinned_notes": [n.content for n in pinned],
        "suggested_question": suggested_question(person, last),
        "draft_message": draft_message(person, last),
    }
