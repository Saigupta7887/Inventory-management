"""Pytest fixtures: an isolated app + TestClient backed by a temp SQLite DB.

Environment is configured BEFORE importing the app so settings pick it up.
"""

import io
import os
import tempfile

import pytest

# --- Configure a clean, isolated environment before importing the app ---
_tmp = tempfile.mkdtemp(prefix="toolinv-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp, 'test.db')}"
os.environ["UPLOAD_DIR"] = os.path.join(_tmp, "uploads")
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-1234567890"
os.environ["ENVIRONMENT"] = "development"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["ANTHROPIC_API_KEY"] = ""  # force the mock vision path

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def register(client, email, password="secret1", name="Test User"):
    r = client.post("/auth/signup", json={"email": email, "password": password, "display_name": name})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_token(client):
    import uuid
    return register(client, f"u{uuid.uuid4().hex[:8]}@test.com")


def jpeg_bytes(color=(120, 120, 120), size=(320, 240)):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()
