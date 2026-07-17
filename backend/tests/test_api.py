"""End-to-end smoke tests. Run with: pytest (uses an in-memory SQLite db)."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Fresh file-backed sqlite per test module run.
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{db_file}")
    with TestClient(app) as c:
        yield c


def _auth(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "u@example.com", "password": "password123", "full_name": "U"},
    )
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_full_flow(client):
    h = _auth(client)

    # Create a person
    r = client.post(
        "/api/people",
        json={"name": "Sarah", "priority": "high", "reminder_interval_days": 7},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    # Add a note -> AI categorization
    r = client.post(
        f"/api/people/{pid}/notes",
        json={"content": "Sarah loves matcha"},
        headers=h,
    )
    assert r.status_code == 201
    assert r.json()["category"] == "preference"

    # Log an interaction -> updates last_interaction_at
    r = client.post(
        f"/api/people/{pid}/interactions",
        json={"channel": "call", "summary": "Caught up", "mood": "positive"},
        headers=h,
    )
    assert r.status_code == 201

    # Aggregations respond
    for path in ["/api/dashboard", "/api/reminders", "/api/insights"]:
        assert client.get(path, headers=h).status_code == 200

    # Search finds by note content
    results = client.get("/api/search", params={"q": "who likes matcha"}, headers=h)
    assert results.status_code == 200
    assert any(r["name"] == "Sarah" for r in results.json()["results"])


def test_auth_required(client):
    assert client.get("/api/people").status_code == 401
