from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..audit import log_audit
from ..database import get_db
from ..deps import get_current_user
from ..models import Item, Location, User
from ..schemas import LocationCreate, LocationOut

router = APIRouter(prefix="/locations", tags=["locations"])


def _owned(db: Session, location_id: str, user: User) -> Location:
    loc = db.get(Location, location_id)
    if loc is None or loc.deleted_at is not None or loc.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Location not found")
    return loc


@router.get("", response_model=list[LocationOut])
def list_locations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Location)
        .filter(Location.owner_id == user.id, Location.deleted_at.is_(None))
        .order_by(Location.created_at.desc())
        .all()
    )


@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    loc = Location(
        owner_id=user.id,
        name=payload.name,
        description=payload.description,
        parent_location_id=payload.parent_location_id,
    )
    db.add(loc)
    db.flush()
    log_audit(db, entity_type="location", entity_id=loc.id, actor_user_id=user.id, action="create")
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from datetime import datetime, timezone

    loc = _owned(db, location_id, user)
    in_use = (
        db.query(Item)
        .filter(Item.location_id == loc.id, Item.deleted_at.is_(None))
        .count()
    )
    if in_use:
        raise HTTPException(status.HTTP_409_CONFLICT, f"{in_use} item(s) still in this location")
    loc.deleted_at = datetime.now(timezone.utc)
    log_audit(db, entity_type="location", entity_id=loc.id, actor_user_id=user.id, action="delete")
    db.commit()
