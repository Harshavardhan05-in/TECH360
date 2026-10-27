import pytest

@pytest.mark.asyncio
async def test_canonical_regions_loaded(client):
    """Verify that all 28 Indian States and 8 Union Territories are populated."""
    response = await client.get("/api/v1/regions")
    assert response.status_code == 200
    regions = response.json()
    assert len(regions) == 36 # 28 states + 8 UTs

    codes = [r["code"] for r in regions]
    assert "IN-TG" in codes # Telangana
    assert "IN-KA" in codes # Karnataka
    assert "IN-DL" in codes # Delhi
    assert "IN-MH" in codes # Maharashtra

@pytest.mark.asyncio
async def test_cross_state_geo_leakage_prevention(client):
    """
    CRITICAL TEST: Ensure physical events from Karnataka NEVER leak into Telangana listings.
    """
    # 1. Query Telangana physical events
    tg_resp = await client.get("/api/v1/events?state_slug=telangana")
    assert tg_resp.status_code == 200
    tg_data = tg_resp.json()
    
    # Must contain Telangana event
    tg_titles = [e["title"] for e in tg_data["items"]]
    assert any("Telangana" in t for t in tg_titles)

    # Must NOT contain Karnataka or Delhi event
    assert not any("Karnataka" in t or "Bengaluru" in t for t in tg_titles)
    assert not any("Delhi" in t for t in tg_titles)
    # Must NOT contain online-only event by default
    assert not any("Autonomous Agents" in t for t in tg_titles)

    # 2. Query Karnataka physical events
    ka_resp = await client.get("/api/v1/events?state_slug=karnataka")
    assert ka_resp.status_code == 200
    ka_data = ka_resp.json()
    ka_titles = [e["title"] for e in ka_data["items"]]
    
    assert any("Bengaluru" in e.get("city", "") or "Karnataka" in e.get("title", "") for e in ka_data["items"])
    assert not any("Telangana" in t for t in ka_titles)

@pytest.mark.asyncio
async def test_online_event_isolation(client):
    """Online events should appear when filtering by format=online, but not in state physical queues."""
    online_resp = await client.get("/api/v1/events?format=online")
    assert online_resp.status_code == 200
    items = online_resp.json()["items"]
    assert any("Autonomous Agents" in e["title"] for e in items)

    # Now verify it does not leak into Telangana physical search
    tg_resp = await client.get("/api/v1/events?state_slug=telangana&include_online=false")
    tg_items = tg_resp.json()["items"]
    for e in tg_items:
        assert e["format"] != "online"
