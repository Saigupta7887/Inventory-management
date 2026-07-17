from tests.conftest import auth, jpeg_bytes


def test_photo_upload_detect_accept_thumb(client, user_token):
    h = auth(user_token)
    loc = client.post("/locations", json={"name": "Workbench"}, headers=h).json()

    up = client.post(
        "/photos",
        headers=h,
        data={"location_id": loc["id"]},
        files={"file": ("desk.jpg", jpeg_bytes(), "image/jpeg")},
    )
    assert up.status_code == 201, up.text
    photo = up.json()

    dets = client.post(f"/photos/{photo['id']}/detect", headers=h).json()
    assert len(dets) >= 1

    ids = [d["id"] for d in dets[:2]]
    items = client.post(
        f"/photos/{photo['id']}/accept",
        json={"detection_ids": ids, "location_id": loc["id"]},
        headers=h,
    ).json()
    assert len(items) == 2

    # Thumbnail served via a short-lived media token (not the session token).
    mt = client.post("/auth/media-token", headers=h).json()["access_token"]
    thumb = client.get(f"/photos/{photo['id']}/thumb", params={"t": mt})
    assert thumb.status_code == 200
    assert thumb.content[:2] == b"\xff\xd8"  # JPEG magic


def test_upload_rejects_non_image(client, user_token):
    h = auth(user_token)
    r = client.post("/photos", headers=h, files={"file": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 415


def test_task_plan_readiness(client, user_token):
    h = auth(user_token)
    plan = client.post("/tasks/plan", json={"task": "change my car tire"}, headers=h).json()
    assert plan["title"]
    assert plan["missing_essential"] >= 1
    assert plan["ready"] is False
    assert len(plan["steps"]) >= 3
    assert plan["video_url"].startswith("https://www.youtube.com")

    loc = client.post("/locations", json={"name": "Trunk"}, headers=h).json()
    for name in ["Car jack", "Lug wrench", "Spare tire"]:
        client.post("/items", json={"name": name, "location_id": loc["id"]}, headers=h)

    plan2 = client.post("/tasks/plan", json={"task": "change my tires"}, headers=h).json()
    assert plan2["ready"] is True
    assert plan2["missing_essential"] == 0
    owned = [t for t in plan2["tools"] if t["owned"]]
    assert any(t["location_name"] == "Trunk" for t in owned)
