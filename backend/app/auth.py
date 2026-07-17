"""Password hashing and JWT token helpers."""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from .config import get_settings

settings = get_settings()

# pbkdf2_sha256 is pure-Python (no native build step) — reliable everywhere.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def _encode(user_id: str, scope: str, minutes: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": user_id, "scope": scope, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(user_id: str) -> str:
    """Full session token used for API calls (sent in the Authorization header)."""
    return _encode(user_id, "session", settings.access_token_expire_minutes)


def create_media_token(user_id: str) -> str:
    """Short-lived, read-only token used ONLY in image URLs.

    Keeps the long-lived session token out of URLs (which leak into browser
    history, referrer headers and server logs).
    """
    return _encode(user_id, "media", settings.media_token_expire_minutes)


def decode_token(token: str, *, scopes: set[str] | None = None) -> str | None:
    """Return the user id (sub) from a valid token, else None.

    If `scopes` is given, the token's scope must be in that set.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
    if scopes is not None and payload.get("scope") not in scopes:
        return None
    return payload.get("sub")
