from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Person(Base):
    """A person the user wants to stay connected with (Phase 2)."""

    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    name: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    relationship_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birthday: Mapped[date | None] = mapped_column(Date, nullable=True)

    # very_high | high | medium | low
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    preferred_contact_method: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    # Days between reconnect reminders (Phase 5)
    reminder_interval_days: Mapped[int] = mapped_column(Integer, default=30)

    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated

    # Where this person is based (Phase 10 — nearby / context-aware reminders).
    location_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    last_interaction_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    owner: Mapped["User"] = relationship(back_populates="people")  # noqa: F821
    notes: Mapped[list["Note"]] = relationship(  # noqa: F821
        back_populates="person", cascade="all, delete-orphan"
    )
    interactions: Mapped[list["Interaction"]] = relationship(  # noqa: F821
        back_populates="person", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(  # noqa: F821
        back_populates="person", cascade="all, delete-orphan"
    )
    errands: Mapped[list["Errand"]] = relationship(  # noqa: F821
        back_populates="person", cascade="all, delete-orphan"
    )
