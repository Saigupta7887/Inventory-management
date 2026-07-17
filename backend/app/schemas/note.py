from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    content: str
    category: str | None = None
    pinned: bool = False


class NoteUpdate(BaseModel):
    content: str | None = None
    category: str | None = None
    pinned: bool | None = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    content: str
    category: str | None
    pinned: bool
    created_at: datetime
