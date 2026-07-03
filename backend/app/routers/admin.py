from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import Item, Location, Photo, User
from ..schemas import AdminAnalytics, UserOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).filter(User.deleted_at.is_(None)).order_by(User.created_at.desc()).all()


@router.get("/analytics", response_model=AdminAnalytics)
def analytics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total_users = db.query(User).filter(User.deleted_at.is_(None)).count()
    items = db.query(Item).filter(Item.deleted_at.is_(None)).all()
    total_locations = db.query(Location).filter(Location.deleted_at.is_(None)).count()
    total_photos = db.query(Photo).filter(Photo.deleted_at.is_(None)).count()

    by_status: Counter = Counter(i.status for i in items)

    # Likely duplicates: same normalized name owned by the same user > once.
    per_owner_name: Counter = Counter((i.owner_id, i.name.strip().lower()) for i in items)
    likely_duplicates = [
        {"name": name, "owner_id": owner, "count": count}
        for (owner, name), count in per_owner_name.items()
        if count > 1
    ]

    name_counts: Counter = Counter(i.name.strip().lower() for i in items)
    most_common_items = [{"name": n, "count": c} for n, c in name_counts.most_common(10)]

    return AdminAnalytics(
        total_users=total_users,
        total_items=len(items),
        total_locations=total_locations,
        total_photos=total_photos,
        items_by_status=dict(by_status),
        likely_duplicates=sorted(likely_duplicates, key=lambda d: -d["count"]),
        most_common_items=most_common_items,
    )
