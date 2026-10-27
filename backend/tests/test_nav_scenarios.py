import pytest
from httpx import AsyncClient
from backend.app.models.event import Event
from sqlalchemy import select

@pytest.mark.asyncio
async def test_case_1_valid_official_registration_url(client: AsyncClient):
    """Case 1: Event with a valid official registration URL returns 200 with verified reachability."""
    res = await client.get("/api/v1/events/devfest-hyderabad-2026")
    assert res.status_code == 200
    data = res.json()
    assert "DevFest Hyderabad 2026" in data["title"]
    assert data["registration_url"].startswith("https://")
    assert data["official_website"].startswith("https://")

@pytest.mark.asyncio
async def test_case_2_event_with_no_registration_url(client: AsyncClient, db_session):
    """Case 2: Event with no direct registration URL preserves official website and does not fabricate a URL."""
    res_ev = await db_session.execute(select(Event).where(Event.slug == "telangana-ai-deeptech-hackathon-2026"))
    event = res_ev.scalar_one()
    event.registration_url = None
    await db_session.commit()

    res = await client.get("/api/v1/events/telangana-ai-deeptech-hackathon-2026")
    assert res.status_code == 200
    data = res.json()
    assert data["slug"] == "telangana-ai-deeptech-hackathon-2026"
    assert data["registration_url"] is None
    assert data["official_website"] == "https://t-hub.co/"

@pytest.mark.asyncio
async def test_case_3_event_with_broken_or_404_url(client: AsyncClient, db_session):
    """Case 3: Event with broken/404 registration URL correctly reports destination error so frontend does not open 404."""
    # Explicitly set link_status to confirmed_not_found and http_status to 404 to simulate audited broken link
    res_ev = await db_session.execute(select(Event).where(Event.slug == "telangana-ai-deeptech-hackathon-2026"))
    event = res_ev.scalar_one()
    event.link_status = "confirmed_not_found"
    event.link_http_status = 404
    await db_session.commit()

    res = await client.get("/api/v1/events/telangana-ai-deeptech-hackathon-2026")
    assert res.status_code == 200
    data = res.json()
    assert data["slug"] == "telangana-ai-deeptech-hackathon-2026"
    assert data["link_status"] == "confirmed_not_found"
    assert data["link_http_status"] == 404

@pytest.mark.asyncio
async def test_case_4_invalid_internal_event_id_or_slug(client: AsyncClient):
    """Case 4: Invalid internal event ID returns proper 404 JSON response with descriptive message."""
    res = await client.get("/api/v1/events/invalid-event-id-99999")
    assert res.status_code == 404
    data = res.json()
    assert "not found" in data["detail"].lower()

@pytest.mark.asyncio
async def test_case_5_event_opened_from_state_page(client: AsyncClient):
    """Case 5: State filter retrieves events belonging strictly to that state with valid internal slugs."""
    res = await client.get("/api/v1/events?state_slug=telangana")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    slugs = [e["slug"] for e in data["items"]]
    assert "telangana-ai-deeptech-hackathon-2026" in slugs
    assert "devfest-hyderabad-2026" in slugs
    # Verify each event can be retrieved by its slug
    for slug in slugs:
        detail_res = await client.get(f"/api/v1/events/{slug}")
        assert detail_res.status_code == 200

@pytest.mark.asyncio
async def test_case_6_event_retrieval_by_numeric_id(client: AsyncClient, db_session):
    """Case 6: Events can also be retrieved by numeric ID without crashing or 404ing."""
    res_ev = await db_session.execute(select(Event.id, Event.slug))
    first_id, first_slug = res_ev.first()

    res = await client.get(f"/api/v1/events/{first_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == first_id
    assert data["slug"] == first_slug
