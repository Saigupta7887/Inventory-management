import re

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Category, Item, Location, User
from ..schemas import ItemOut, SearchResult

router = APIRouter(prefix="/search", tags=["search"])

# Words to strip so "where is my hammer?" -> "hammer".
_STOPWORDS = {
    "where", "is", "are", "my", "the", "a", "an", "do", "i", "have", "any",
    "find", "locate", "whats", "what", "was", "did", "put", "keep", "of",
    "in", "on", "to", "me", "show", "can", "you", "please",
}


def _keywords(q: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", q.lower())
    return [t for t in tokens if t not in _STOPWORDS] or tokens


@router.get("", response_model=list[SearchResult])
def search(q: str = "", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Natural-language / keyword search across the user's items.

    Handles phrasing like "where is my hammer?" by stripping filler words and
    matching remaining keywords against item names, categories and locations.
    """
    query = db.query(Item).filter(Item.owner_id == user.id, Item.deleted_at.is_(None))

    keywords = _keywords(q) if q.strip() else []
    if keywords:
        conditions = []
        for kw in keywords:
            like = f"%{kw}%"
            conditions.append(Item.name.ilike(like))
            conditions.append(Item.notes.ilike(like))
        query = query.filter(or_(*conditions))

    items = query.order_by(Item.created_at.desc()).all()

    # Also allow matching by category name (resolve after the fact).
    if keywords and not items:
        cat_ids = [
            c.id
            for c in db.query(Category).filter(
                or_(*[Category.name.ilike(f"%{kw}%") for kw in keywords])
            )
        ]
        if cat_ids:
            items = (
                db.query(Item)
                .filter(
                    Item.owner_id == user.id,
                    Item.deleted_at.is_(None),
                    Item.category_id.in_(cat_ids),
                )
                .all()
            )

    results: list[SearchResult] = []
    loc_cache: dict[str, str] = {}
    cat_cache: dict[str, str] = {}
    for item in items:
        loc_name = None
        if item.location_id:
            if item.location_id not in loc_cache:
                loc = db.get(Location, item.location_id)
                loc_cache[item.location_id] = loc.name if loc else None
            loc_name = loc_cache[item.location_id]
        cat_name = None
        if item.category_id:
            if item.category_id not in cat_cache:
                cat = db.get(Category, item.category_id)
                cat_cache[item.category_id] = cat.name if cat else None
            cat_name = cat_cache[item.category_id]
        results.append(
            SearchResult(
                item=ItemOut.model_validate(item),
                location_name=loc_name,
                category_name=cat_name,
                photo_id=item.primary_photo_id,
            )
        )
    return results
