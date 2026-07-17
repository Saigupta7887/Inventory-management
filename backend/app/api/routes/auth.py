from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import (
    AppleAuthIn,
    GoogleAuthIn,
    Token,
    UserCreate,
    UserOut,
    UserPreferences,
)
from app.services.oauth import (
    OAuthError,
    OAuthNotConfigured,
    verify_apple_token,
    verify_google_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email))
    if user and user.hashed_password and verify_password(password, user.hashed_password):
        return user
    return None


def _find_or_create_social_user(
    db: Session, profile: dict, provider: str
) -> User:
    """Find a user by email or create one from a verified social profile."""
    user = db.scalar(select(User).where(User.email == profile["email"]))
    if user is None:
        user = User(
            email=profile["email"],
            full_name=profile.get("name"),
            avatar_url=profile.get("picture"),
            provider=provider,
            provider_sub=profile.get("sub"),
            onboarded=False,
        )
        db.add(user)
    else:
        # Link the social identity to the existing account.
        if not user.provider_sub:
            user.provider_sub = profile.get("sub")
        if user.provider == "email":
            user.provider = provider
        if not user.avatar_url and profile.get("picture"):
            user.avatar_url = profile["picture"]
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    # OAuth2PasswordRequestForm uses `username`; we treat it as the email.
    user = _authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(user.id)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/providers")
def providers() -> dict:
    """Which social providers are configured — lets the UI show the right buttons."""
    return {
        "google": bool(settings.google_client_id),
        "apple": bool(settings.apple_client_id_list),
    }


@router.post("/google", response_model=Token)
def google_login(payload: GoogleAuthIn, db: Session = Depends(get_db)) -> Token:
    try:
        profile = verify_google_token(payload.credential)
    except OAuthNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    user = _find_or_create_social_user(db, profile, "google")
    return Token(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/apple", response_model=Token)
def apple_login(payload: AppleAuthIn, db: Session = Depends(get_db)) -> Token:
    try:
        profile = verify_apple_token(payload.identity_token)
    except OAuthNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    if payload.full_name and not profile.get("name"):
        profile["name"] = payload.full_name
    user = _find_or_create_social_user(db, profile, "apple")
    return Token(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)


@router.patch("/me", response_model=UserOut)
def update_preferences(
    payload: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)
