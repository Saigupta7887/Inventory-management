from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Interaction(Base):
    """A logged interaction with a person (Phase 4)."""

    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"), index=True
    )

    # call | text | meeting | email | other
    channel: Mapped[str] = mapped_column(String(30), default="other")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    # positive | neutral | negative
    mood: Mapped[str | None] = mapped_column(String(20), nullable=True)
    follow_up: Mapped[str | None] = mapped_column(Text, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    person: Mapped["Person"] = relationship(  # noqa: F821
        back_populates="interactions"
    )
