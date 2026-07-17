from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    """A memory / fact about a person (Phase 3)."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"), index=True
    )

    content: Mapped[str] = mapped_column(Text)
    # AI categorization (Phase 3): preference | work_update | follow_up | fact | other
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    person: Mapped["Person"] = relationship(back_populates="notes")  # noqa: F821
