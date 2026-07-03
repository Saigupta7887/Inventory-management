"""Seed baseline data on startup: global categories + the admin account."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import hash_password
from .config import get_settings
from .models import Category, User

GLOBAL_CATEGORIES = [
    "Hand tool",
    "Power tool",
    "Screwdriver",
    "Wrench",
    "Pliers",
    "Hammer",
    "Measuring",
    "Cutting",
    "Hardware",
    "Fastener",
    "Electrical",
    "Painting",
    "Gardening",
    "Safety",
    "Other",
]


def seed(db: Session) -> None:
    settings = get_settings()

    existing = {c.name for c in db.query(Category).filter(Category.is_global.is_(True))}
    for name in GLOBAL_CATEGORIES:
        if name not in existing:
            db.add(Category(name=name, is_global=True))

    admin = (
        db.query(User)
        .filter(func.lower(User.email) == settings.admin_email.lower())
        .first()
    )
    if admin is None:
        db.add(
            User(
                email=settings.admin_email.lower(),
                password_hash=hash_password(settings.admin_password),
                display_name="Administrator",
                role="admin",
            )
        )
    db.commit()
