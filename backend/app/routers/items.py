from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..audit import log_audit
from ..database import get_db
from ..deps import get_current_user
from ..models import Item, User
from ..schemas import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

VALID_STATUSES = {"available", "lent_out", "lost", "needs_repair"}


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
