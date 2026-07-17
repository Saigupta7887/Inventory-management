from tests.conftest import auth


def test_item_crud_and_status(client, user_token):
    h = auth(user_token)
    loc = client.post("/locations", json={"name": "Garage"}, headers=h).json()
    created = client.post("/items", json={"name": "Claw hammer", "location_id": loc["id"]}, headers=h)
    assert created.status_code == 201
    item = created.json()
    assert item["status"] == "available"
    # UUIDv7 primary key
    assert item["id"][14] == "7"

    listed = client.get("/items", headers=h).json()
    assert any(i["id"] == item["id"] for i in listed)

    upd = client.patch(f"/items/{item['id']}", json={"status": "lent_out", "lent_to": "Bob"}, headers=h)
    assert upd.status_code == 200 and upd.json()["status"] == "lent_out"

    bad = client.patch(f"/items/{item['id']}", json={"status": "banana"}, headers=h)
    assert bad.status_code == 422

    assert client.delete(f"/items/{item['id']}", headers=h).status_code == 204
    assert client.get(f"/items/{item['id']}", headers=h).status_code == 404


def test_items_are_isolated_per_user(client, user_token):
    h1 = auth(user_token)
    client.post("/items", json={"name": "Private drill"}, headers=h1)
    import uuid
    from tests.conftest import register
    other = register(client, f"o{uuid.uuid4().hex[:6]}@test.com")
    listed = client.get("/items", headers=auth(other)).json()
    assert listed == []


def test_ownership_check(client, user_token):
    h = auth(user_token)
    loc = client.post("/locations", json={"name": "Shed"}, headers=h).json()
    client.post("/items", json={"name": "Adjustable wrench", "location_id": loc["id"]}, headers=h)

    owned = client.get("/items/check", params={"q": "do I own a wrench?"}, headers=h).json()
    assert owned["owned"] is True
    assert owned["verdict"] == "owned"
    assert owned["matches"][0]["location_name"] == "Shed"

    not_owned = client.get("/items/check", params={"q": "chainsaw"}, headers=h).json()
    assert not_owned["owned"] is False
    assert not_owned["verdict"] == "not_owned"


def test_items_pagination(client, user_token):
    h = auth(user_token)
    for i in range(5):
        client.post("/items", json={"name": f"Tool {i}"}, headers=h)
    page = client.get("/items", params={"limit": 2, "offset": 0}, headers=h).json()
    assert len(page) == 2
