from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InteractionCreate(BaseModel):
    channel: str = "other"
    summary: str | None = None
    mood: str | None = None
    follow_up: str | None = None
    occurred_at: datetime | None = None


class InteractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    channel: str
    summary: str | None
    mood: str | None
    follow_up: str | None
    occurred_at: datetime
