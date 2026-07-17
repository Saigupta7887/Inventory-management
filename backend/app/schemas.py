"""Pydantic request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- Auth ----
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMModel):
    id: str
    email: str
    display_name: str
    role: str
    created_at: datetime


# ---- Location ----
class LocationCreate(BaseModel):
    name: str
    description: str = ""
    parent_location_id: str | None = None


class LocationOut(ORMModel):
    id: str
    name: str
    description: str
    parent_location_id: str | None
    created_at: datetime


# ---- Category ----
class CategoryCreate(BaseModel):
    name: str
    parent_category_id: str | None = None


class CategoryOut(ORMModel):
    id: str
    name: str
    parent_category_id: str | None
    is_global: bool


# ---- Item ----
class ItemCreate(BaseModel):
    name: str
    category_id: str | None = None
    location_id: str | None = None
    primary_photo_id: str | None = None
    source_detection_id: str | None = None
    quantity: int = 1
    notes: str = ""


class ItemUpdate(BaseModel):
    name: str | None = None
    category_id: str | None = None
    location_id: str | None = None
    quantity: int | None = None
    status: str | None = None
    lent_to: str | None = None
    notes: str | None = None


class ItemOut(ORMModel):
    id: str
    name: str
    category_id: str | None
    location_id: str | None
    primary_photo_id: str | None
    quantity: int
    status: str
    lent_to: str | None
    notes: str
    created_at: datetime


# ---- Photo / Detection ----
class PhotoOut(ORMModel):
    id: str
    location_id: str | None
    storage_key: str
    status: str
    width: int
    height: int
    created_at: datetime


class DetectionOut(ORMModel):
    id: str
    photo_id: str
    label: str
    suggested_category: str
    confidence: float
    bbox: dict | None
    status: str
    item_id: str | None


class AcceptDetectionsRequest(BaseModel):
    detection_ids: list[str]
    location_id: str | None = None


# ---- Search ----
class SearchResult(BaseModel):
    item: ItemOut
    location_name: str | None
    category_name: str | None
    photo_id: str | None


# ---- Ownership check ("before you buy") ----
class OwnershipMatch(BaseModel):
    id: str
    name: str
    location_name: str | None
    status: str
    quantity: int
    photo_id: str | None


class OwnershipCheck(BaseModel):
    query: str
    owned: bool
    total_quantity: int
    matches: list[OwnershipMatch]
    verdict: str  # "owned" | "not_owned"
    message: str


# ---- Task assistant ("how do I …") ----
class TaskPlanRequest(BaseModel):
    task: str


class TaskToolNeed(BaseModel):
    name: str
    category: str
    essential: bool
    owned: bool
    location_name: str | None
    item_id: str | None


class TaskPlanResponse(BaseModel):
    task: str
    title: str
    tools: list[TaskToolNeed]
    steps: list[str]
    safety: list[str]
    ready: bool
    missing_essential: int
    missing_total: int
    video_query: str
    video_url: str
    engine: str


# ---- Admin ----
class AdminAnalytics(BaseModel):
    total_users: int
    total_items: int
    total_locations: int
    total_photos: int
    items_by_status: dict[str, int]
    likely_duplicates: list[dict]
    most_common_items: list[dict]
