"""End-to-end smoke tests. Run with: pytest (uses an in-memory SQLite db)."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    # Reset the schema before each test for full isolation. The engine is
    # created once at import time from DATABASE_URL (SQLite here).
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
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


def test_location_feature(client):
    h = _auth(client)

    # A person based in downtown San Francisco.
    r = client.post(
        "/api/people",
        json={
            "name": "Sarah",
            "latitude": 37.7793,
            "longitude": -122.4192,
            "location_label": "SF",
        },
        headers=h,
    )
    pid = r.json()["id"]

    # An errand for Sarah, to do at a grocery store.
    r = client.post(
        "/api/errands",
        json={"title": "Pick up matcha", "place_type": "grocery", "person_id": pid},
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert r.json()["person_name"] == "Sarah"

    # A saved grocery store near downtown SF.
    r = client.post(
        "/api/places",
        json={
            "name": "Corner Market",
            "place_type": "grocery",
            "latitude": 37.7794,
            "longitude": -122.4191,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text

    # Manual check-in surfaces the grocery errand.
    r = client.get("/api/nearby/check-in", params={"place_type": "grocery"}, headers=h)
    assert r.status_code == 200
    assert any(e["title"] == "Pick up matcha" for e in r.json()["errands"])

    # GPS nearby (standing next to the market) surfaces the place + errand + Sarah.
    r = client.get(
        "/api/nearby",
        params={"lat": 37.7793, "lng": -122.4192, "radius_km": 2},
        headers=h,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["nearby_places"]) == 1
    assert body["nearby_places"][0]["errands"][0]["title"] == "Pick up matcha"
    assert any(p["name"] == "Sarah" for p in body["nearby_people"])

    # Standing far away (New York) surfaces nothing.
    r = client.get(
        "/api/nearby",
        params={"lat": 40.7128, "lng": -74.0060, "radius_km": 2},
        headers=h,
    )
    assert r.json()["nearby_places"] == []
    assert r.json()["nearby_people"] == []
