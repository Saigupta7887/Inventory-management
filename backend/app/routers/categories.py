from fastapi import APIRouter, Depends, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Category, User
from ..schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Global categories plus this user's own custom categories."""
    return (
        db.query(Category)
        .filter(
            Category.deleted_at.is_(None),
            or_(Category.is_global.is_(True), Category.owner_id == user.id),
        )
        .order_by(Category.name.asc())
        .all()
    )


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cat = Category(
        name=payload.name,
        parent_category_id=payload.parent_category_id,
        is_global=False,
        owner_id=user.id,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat
