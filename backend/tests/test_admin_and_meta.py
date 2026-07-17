from tests.conftest import auth


def test_health_and_ready(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ready"


def test_admin_requires_admin_role(client, user_token):
    # A regular customer must not reach admin endpoints.
    assert client.get("/admin/analytics", headers=auth(user_token)).status_code == 403
    assert client.get("/admin/users", headers=auth(user_token)).status_code == 403


def test_admin_analytics(client):
    login = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin1234"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    an = client.get("/admin/analytics", headers=auth(token))
    assert an.status_code == 200
    body = an.json()
    assert "total_users" in body and "items_by_status" in body


def test_security_headers(client):
    r = client.get("/health")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "X-Request-ID" in r.headers
