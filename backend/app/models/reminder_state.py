from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReminderState(Base):
    """Tracks snooze/complete actions on computed reminders (Phase 5).

    Reminders themselves are derived on the fly (reconnect / birthday); this
    records the user's action on a given (person, kind) pair so the Snoozed and
    Completed tabs persist.
    """

    __tablename__ = "reminder_states"
    __table_args__ = (
        UniqueConstraint("owner_id", "person_id", "kind", name="uq_reminder_state"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id", ondelete="CASCADE"), index=True
    )
    # reconnect | birthday
    kind: Mapped[str] = mapped_column(String(30))
    # active | snoozed | completed
    status: Mapped[str] = mapped_column(String(20), default="active")
    snoozed_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
