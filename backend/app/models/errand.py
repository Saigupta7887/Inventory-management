from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Errand(Base):
    """Something to pick up / do for someone at a type of place (Phase 10).

    Example: "Pick up matcha for Sarah" with place_type="grocery". When the
    user is at (or checks in to) a grocery store, this surfaces.
    """

    __tablename__ = "errands"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Optional: the person this errand is for.
    person_id: Mapped[int | None] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255))
    # grocery | pharmacy | cafe | gym | bookstore | restaurant | other
    place_type: Mapped[str] = mapped_column(String(40), default="other")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    person: Mapped["Person"] = relationship(back_populates="errands")  # noqa: F821
