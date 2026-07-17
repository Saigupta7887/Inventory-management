from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ErrandCreate(BaseModel):
    title: str
    place_type: str = "other"
    person_id: int | None = None
    note: str | None = None


class ErrandUpdate(BaseModel):
    title: str | None = None
    place_type: str | None = None
    person_id: int | None = None
    note: str | None = None
    completed: bool | None = None


class ErrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int | None
    person_name: str | None = None
    title: str
    place_type: str
    note: str | None
    completed: bool
    created_at: datetime
