"""Helper to append to the audit log — every mutation is recorded by UUID."""

from sqlalchemy.orm import Session

from .models import AuditLog


def log_audit(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    actor_user_id: str | None,
    action: str,
    diff: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            action=action,
            diff=diff,
        )
    )
