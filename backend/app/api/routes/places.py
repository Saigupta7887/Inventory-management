from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.place import Place
from app.models.user import User
from app.schemas.place import PlaceCreate, PlaceOut

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("", response_model=list[PlaceOut])
def list_places(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Place]:
    return list(
        db.scalars(
            select(Place).where(Place.owner_id == user.id).order_by(Place.name)
        )
    )


@router.post("", response_model=PlaceOut, status_code=status.HTTP_201_CREATED)
def create_place(
    payload: PlaceCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Place:
    place = Place(owner_id=user.id, **payload.model_dump())
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    place_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    place = db.get(Place, place_id)
    if place is None or place.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Place not found")
    db.delete(place)
    db.commit()
