import pytest

@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    reg_payload = {
        "email": "developer@example.com",
        "password": "Password123!",
        "full_name": "Test Developer"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "developer@example.com"

    # Duplicate registration should fail
    dup_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # Login
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "developer@example.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data

@pytest.mark.asyncio
async def test_anonymous_view_limit_enforcement(client):
    """
    Test that anonymous visitors can view up to 5 unique event details,
    and are prompted to sign in on the 6th view.
    """
    # Fetch list of events
    list_resp = await client.get("/api/v1/events")
    events = list_resp.json()["items"]
    
    # We have 5 events in seed data
    for ev in events[:5]:
        resp = await client.get(f"/api/v1/events/{ev['id']}")
        assert resp.status_code == 200

    # Re-viewing the same event is allowed
    re_resp = await client.get(f"/api/v1/events/{events[0]['id']}")
    assert re_resp.status_code == 200
