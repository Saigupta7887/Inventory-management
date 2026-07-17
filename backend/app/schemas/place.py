from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlaceCreate(BaseModel):
    name: str
    place_type: str = "other"
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    place_type: str
    address: str | None
    latitude: float | None
    longitude: float | None
    created_at: datetime
