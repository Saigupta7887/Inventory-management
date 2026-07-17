from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PersonBase(BaseModel):
    name: str
    nickname: str | None = None
    relationship_type: str | None = None
    phone: str | None = None
    email: str | None = None
    birthday: date | None = None
    priority: str = "medium"
    preferred_contact_method: str | None = None
    reminder_interval_days: int = 30
    tags: str | None = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: str | None = None
    nickname: str | None = None
    relationship_type: str | None = None
    phone: str | None = None
    email: str | None = None
    birthday: date | None = None
    priority: str | None = None
    preferred_contact_method: str | None = None
    reminder_interval_days: int | None = None
    tags: str | None = None


class PersonOut(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_interaction_at: datetime | None
    created_at: datetime
