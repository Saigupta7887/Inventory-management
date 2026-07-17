import uuid

from tests.conftest import auth, register


def test_signup_login_me(client):
    email = f"a{uuid.uuid4().hex[:8]}@test.com"
    token = register(client, email)
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["email"] == email
    assert me.json()["role"] == "customer"

    login = client.post("/auth/login", json={"email": email, "password": "secret1"})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_duplicate_email_conflict(client):
    email = f"dup{uuid.uuid4().hex[:6]}@test.com"
    register(client, email)
    r = client.post("/auth/signup", json={"email": email, "password": "secret1", "display_name": "X"})
    assert r.status_code == 409


def test_login_wrong_password(client):
    email = f"wp{uuid.uuid4().hex[:6]}@test.com"
    register(client, email)
    r = client.post("/auth/login", json={"email": email, "password": "nope"})
    assert r.status_code == 401


def test_no_token_rejected(client):
    assert client.get("/auth/me").status_code == 401


def test_media_token_cannot_access_api(client, user_token):
    """A media token is read-only and must not authenticate API calls."""
    mt = client.post("/auth/media-token", headers=auth(user_token)).json()["access_token"]
    r = client.get("/auth/me", headers=auth(mt))
    assert r.status_code == 401
