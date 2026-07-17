from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.errand import Errand
from app.models.person import Person
from app.models.user import User
from app.schemas.errand import ErrandCreate, ErrandOut, ErrandUpdate

router = APIRouter(prefix="/api/errands", tags=["errands"])


def _to_out(errand: Errand, db: Session) -> ErrandOut:
    person_name = None
    if errand.person_id:
        person = db.get(Person, errand.person_id)
        person_name = person.name if person else None
    data = ErrandOut.model_validate(errand)
    data.person_name = person_name
    return data


@router.get("", response_model=list[ErrandOut])
def list_errands(
    place_type: str | None = Query(default=None),
    include_completed: bool = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ErrandOut]:
    stmt = select(Errand).where(Errand.owner_id == user.id)
    if place_type:
        stmt = stmt.where(Errand.place_type == place_type)
    if not include_completed:
        stmt = stmt.where(Errand.completed.is_(False))
    stmt = stmt.order_by(Errand.created_at.desc())
    return [_to_out(e, db) for e in db.scalars(stmt)]


@router.post("", response_model=ErrandOut, status_code=status.HTTP_201_CREATED)
def create_errand(
    payload: ErrandCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ErrandOut:
    if payload.person_id is not None:
        person = db.get(Person, payload.person_id)
        if person is None or person.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Person not found")
    errand = Errand(owner_id=user.id, **payload.model_dump())
    db.add(errand)
    db.commit()
    db.refresh(errand)
    return _to_out(errand, db)


@router.patch("/{errand_id}", response_model=ErrandOut)
def update_errand(
    errand_id: int,
    payload: ErrandUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ErrandOut:
    errand = db.get(Errand, errand_id)
    if errand is None or errand.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Errand not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(errand, field, value)
    db.commit()
    db.refresh(errand)
    return _to_out(errand, db)


@router.delete("/{errand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_errand(
    errand_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    errand = db.get(Errand, errand_id)
    if errand is None or errand.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Errand not found")
    db.delete(errand)
    db.commit()
