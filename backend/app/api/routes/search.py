from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.note import Note
from app.models.person import Person
from app.models.user import User

router = APIRouter(prefix="/api/search", tags=["search"])

_STOPWORDS = {
    "who", "what", "when", "likes", "like", "has", "have", "is", "the", "a",
    "an", "mentioned", "next", "this", "month", "about", "of", "to", "in",
}


@router.get("")
def search(
    q: str = Query(..., min_length=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Natural-language-ish search over people and notes (Phase 9).

    Strips common question words and matches the remaining keywords against
    person names, tags, and note contents.
    """
    keywords = [w for w in q.lower().split() if w not in _STOPWORDS and len(w) > 1]
    if not keywords:
        keywords = q.lower().split()

    owned = select(Person.id).where(Person.owner_id == user.id).subquery()

    people_hits: dict[int, Person] = {}
    for kw in keywords:
        pattern = f"%{kw}%"
        # People matched by name / nickname / tags
        for p in db.scalars(
            select(Person).where(
                Person.owner_id == user.id,
                or_(
                    Person.name.ilike(pattern),
                    Person.nickname.ilike(pattern),
                    Person.tags.ilike(pattern),
                ),
            )
        ):
            people_hits[p.id] = p

        # People matched via their notes
        for note in db.scalars(
            select(Note).where(
                Note.person_id.in_(select(owned.c.id)),
                Note.content.ilike(pattern),
            )
        ):
            person = db.get(Person, note.person_id)
            if person:
                people_hits[person.id] = person

    return {
        "query": q,
        "keywords": keywords,
        "results": [
            {
                "person_id": p.id,
                "name": p.name,
                "relationship_type": p.relationship_type,
                "tags": p.tags,
            }
            for p in people_hits.values()
        ],
    }
