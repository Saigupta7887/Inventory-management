"""SQLAlchemy models — UUID-first data model.

Every entity uses a UUIDv7 string primary key and carries the same base
fields (timestamps, soft-delete marker, optimistic-concurrency version).
Relationships are expressed as UUID foreign keys, so the ID is the contract
between modules and could later be split across services without change.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .ids import new_id


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class BaseEntity:
    """Mixin applied to every table: UUID PK + audit/versioning columns."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)


class User(BaseEntity, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default="customer")  # customer | admin


class Location(BaseEntity, Base):
    __tablename__ = "locations"

    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    parent_location_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True
    )


class Category(BaseEntity, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(120))
    parent_category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=True
    )
    is_global: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )


class Photo(BaseEntity, Base):
    __tablename__ = "photos"

    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    location_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True
    )
    storage_key: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(80), default="image/jpeg")
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded|processing|processed|failed

    detections: Mapped[list["Detection"]] = relationship(
        back_populates="photo", cascade="all, delete-orphan"
    )


class Detection(BaseEntity, Base):
    """A single tool proposed by the vision model for a photo (pre-confirmation)."""

    __tablename__ = "detections"

    photo_id: Mapped[str] = mapped_column(String(36), ForeignKey("photos.id"), index=True)
    label: Mapped[str] = mapped_column(String(160))
    suggested_category: Mapped[str] = mapped_column(String(120), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    bbox: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {x,y,w,h} normalized 0..1
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|accepted|rejected
    item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("items.id"), nullable=True
    )

    photo: Mapped["Photo"] = relationship(back_populates="detections")


class Item(BaseEntity, Base):
    """A real, owned tool."""

    __tablename__ = "items"

    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id"), nullable=True
    )
    location_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("locations.id"), nullable=True, index=True
    )
    primary_photo_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("photos.id"), nullable=True
    )
    source_detection_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="available")  # available|lent_out|lost|needs_repair
    lent_to: Mapped[str | None] = mapped_column(String(160), nullable=True)
    lent_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class AuditLog(BaseEntity, Base):
    __tablename__ = "audit_log"

    entity_type: Mapped[str] = mapped_column(String(60), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(40))
    diff: Mapped[dict | None] = mapped_column(JSON, nullable=True)
