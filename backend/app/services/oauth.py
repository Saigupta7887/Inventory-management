"""Verification of Google and Apple identity tokens (Phase 1 social login).

Each verifier returns a normalized profile dict:
    {"sub": str, "email": str, "name": str | None, "picture": str | None}

They raise:
    OAuthNotConfigured — the provider has no client ID set (feature disabled)
    OAuthError         — the token was present but invalid / untrusted
"""

from __future__ import annotations

import json
import time
import urllib.request

from jose import jwt

from app.core.config import settings

APPLE_ISSUER = "https://appleid.apple.com"
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"


class OAuthError(Exception):
    pass


class OAuthNotConfigured(OAuthError):
    pass


# ---- Google ---------------------------------------------------------------


def verify_google_token(credential: str) -> dict:
    if not settings.google_client_id:
        raise OAuthNotConfigured("Google sign-in is not configured on the server.")

    # Imported lazily so the app runs even if google-auth isn't installed yet.
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    try:
        info = id_token.verify_oauth2_token(
            credential, google_requests.Request(), settings.google_client_id
        )
    except ValueError as exc:  # bad signature, wrong audience, expired, etc.
        raise OAuthError("Invalid Google token.") from exc

    if not info.get("email"):
        raise OAuthError("Google token did not include an email.")

    return {
        "sub": info["sub"],
        "email": info["email"].lower(),
        "name": info.get("name"),
        "picture": info.get("picture"),
    }


# ---- Apple ----------------------------------------------------------------

_apple_keys_cache: dict = {"keys": None, "fetched_at": 0.0}


def _apple_keys() -> list[dict]:
    now = time.time()
    if _apple_keys_cache["keys"] and now - _apple_keys_cache["fetched_at"] < 3600:
        return _apple_keys_cache["keys"]
    with urllib.request.urlopen(APPLE_KEYS_URL, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    _apple_keys_cache["keys"] = data["keys"]
    _apple_keys_cache["fetched_at"] = now
    return data["keys"]


def verify_apple_token(identity_token: str) -> dict:
    audiences = settings.apple_client_id_list
    if not audiences:
        raise OAuthNotConfigured("Apple sign-in is not configured on the server.")

    try:
        header = jwt.get_unverified_header(identity_token)
    except Exception as exc:  # noqa: BLE001
        raise OAuthError("Malformed Apple token.") from exc

    key = next((k for k in _apple_keys() if k["kid"] == header.get("kid")), None)
    if key is None:
        raise OAuthError("Apple signing key not found.")

    try:
        claims = jwt.decode(
            identity_token,
            key,
            algorithms=["RS256"],
            audience=audiences,
            issuer=APPLE_ISSUER,
        )
    except Exception as exc:  # noqa: BLE001
        raise OAuthError("Invalid Apple token.") from exc

    if not claims.get("email"):
        raise OAuthError("Apple token did not include an email.")

    return {
        "sub": claims["sub"],
        "email": claims["email"].lower(),
        "name": None,  # Apple only sends the name on first consent, out-of-band.
        "picture": None,
    }
