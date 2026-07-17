from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPreferences(BaseModel):
    reminder_style: str | None = None  # gentle | balanced | active
    ai_suggestions_enabled: bool | None = None
    onboarded: bool | None = None
    full_name: str | None = None


class GoogleAuthIn(BaseModel):
    credential: str  # the Google ID token from Google Identity Services


class AppleAuthIn(BaseModel):
    identity_token: str
    full_name: str | None = None  # Apple only provides this on first sign-in


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    provider: str
    avatar_url: str | None
    reminder_style: str
    ai_suggestions_enabled: bool
    onboarded: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
