from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy import or_

from ..audit import log_audit
from ..database import get_db
from ..deps import get_current_user
from ..models import Category, Item, Location, User
from ..schemas import ItemCreate, ItemOut, ItemUpdate, OwnershipCheck, OwnershipMatch

router = APIRouter(prefix="/items", tags=["items"])

VALID_STATUSES = {"available", "lent_out", "lost", "needs_repair"}

# Filler words stripped from a "do I own a …?" style query.
_CHECK_STOPWORDS = {
    "a", "an", "the", "do", "i", "own", "have", "any", "another", "new",
    "should", "buy", "need", "get", "is", "there", "some", "my",
}


def _owned(db: Session, item_id: str, user: User) -> Item:
    item = db.get(Item, item_id)
    if item is None or item.deleted_at is not None or item.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


@router.get("", response_model=list[ItemOut])
def list_items(
    location_id: str | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Item).filter(Item.owner_id == user.id, Item.deleted_at.is_(None))
    if location_id:
        q = q.filter(Item.location_id == location_id)
    if status_filter:
        q = q.filter(Item.status == status_filter)
    return q.order_by(Item.created_at.desc()).all()


@router.get("/check", response_model=OwnershipCheck)
def ownership_check(
    q: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """"Before you buy" — tell the user whether they already own a tool.

    Answers the core question the app exists for: search a tool name and get a
    clear verdict ("You already own it, here's where" vs "safe to buy").
    """
    import re

    tokens = re.findall(r"[a-zA-Z0-9]+", q.lower())
    keywords = [t for t in tokens if t not in _CHECK_STOPWORDS] or tokens

    items: list[Item] = []
    if keywords:
        conditions = [Item.name.ilike(f"%{kw}%") for kw in keywords]
        # Also match items whose category name contains a keyword.
        cat_ids = [
            c.id
            for c in db.query(Category).filter(
                or_(*[Category.name.ilike(f"%{kw}%") for kw in keywords])
            )
        ]
        if cat_ids:
            conditions.append(Item.category_id.in_(cat_ids))
        items = (
            db.query(Item)
            .filter(
                Item.owner_id == user.id,
                Item.deleted_at.is_(None),
                or_(*conditions),
            )
            .order_by(Item.created_at.desc())
            .all()
        )

    loc_cache: dict[str, str | None] = {}

    def loc_name(loc_id: str | None) -> str | None:
        if not loc_id:
            return None
        if loc_id not in loc_cache:
            loc = db.get(Location, loc_id)
            loc_cache[loc_id] = loc.name if loc else None
        return loc_cache[loc_id]

    matches = [
        OwnershipMatch(
            id=it.id,
            name=it.name,
            location_name=loc_name(it.location_id),
            status=it.status,
            quantity=it.quantity,
            photo_id=it.primary_photo_id,
        )
        for it in items
    ]
    total_qty = sum(it.quantity for it in items)
    owned = len(items) > 0
    label = q.strip() or "that tool"

    if owned:
        first = matches[0]
        where = f" in {first.location_name}" if first.location_name else ""
        extra = f" (and {len(matches) - 1} more)" if len(matches) > 1 else ""
        message = f"You already own {total_qty}{where}{extra}. No need to buy another."
    else:
        message = f"No match for “{label}”. You don't seem to own one — safe to buy."

    return OwnershipCheck(
        query=q,
        owned=owned,
        total_quantity=total_qty,
        matches=matches,
        verdict="owned" if owned else "not_owned",
        message=message,
    )


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = Item(
        owner_id=user.id,
        name=payload.name,
        category_id=payload.category_id,
        location_id=payload.location_id,
        primary_photo_id=payload.primary_photo_id,
        source_detection_id=payload.source_detection_id,
        quantity=payload.quantity,
        notes=payload.notes,
    )
    db.add(item)
    db.flush()
    log_audit(db, entity_type="item", entity_id=item.id, actor_user_id=user.id, action="create")
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _owned(db, item_id, user)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = _owned(db, item_id, user)
    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] not in VALID_STATUSES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid status")

    # Manage lent-out bookkeeping.
    if data.get("status") == "lent_out" and item.status != "lent_out":
        item.lent_since = datetime.now(timezone.utc)
    if data.get("status") and data["status"] != "lent_out":
        item.lent_to = None
        item.lent_since = None

    for field, value in data.items():
        setattr(item, field, value)
    item.version += 1
    log_audit(
        db, entity_type="item", entity_id=item.id, actor_user_id=user.id,
        action="update", diff=data,
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = _owned(db, item_id, user)
    item.deleted_at = datetime.now(timezone.utc)
    log_audit(db, entity_type="item", entity_id=item.id, actor_user_id=user.id, action="delete")
    db.commit()
