from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReminderCreate(BaseModel):
    kind: str = "reconnect"
    message: str | None = None
    due_at: datetime


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    kind: str
    message: str | None
    due_at: datetime
    completed: bool
    created_at: datetime


class ReminderWithPerson(ReminderOut):
    person_name: str
