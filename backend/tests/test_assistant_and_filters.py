import pytest
from unittest.mock import patch, AsyncMock
from backend.app.schemas.assistant import AssistantQueryRequest, ChatMessage
from backend.app.services.assistant_service import execute_assistant_query

@pytest.mark.asyncio
async def test_assistant_greeting(client, db_session):
    """Verify assistant responds naturally to 'Hi' without forcing an event dump."""
    res = await client.post("/api/v1/assistant/query", json={"query": "Hi"})
    assert res.status_code == 200
    data = res.json()
    assert "Hi!" in data["answer"] or "help" in data["answer"].lower()
    assert data["intent"] == "greeting"
    assert len(data["events"]) == 0

@pytest.mark.asyncio
async def test_assistant_how_are_you(client):
    """Verify assistant responds politely to 'How are you?'."""
    res = await client.post("/api/v1/assistant/query", json={"query": "How are you?"})
    assert res.status_code == 200
    data = res.json()
    assert "doing well" in data["answer"].lower() or "ready" in data["answer"].lower()
    assert data["intent"] == "status"
    assert len(data["events"]) == 0

@pytest.mark.asyncio
async def test_assistant_capabilities(client):
    """Verify assistant explains what it can do upon user inquiry."""
    res = await client.post("/api/v1/assistant/query", json={"query": "What can you do?"})
    assert res.status_code == 200
    data = res.json()
    assert "EventHorizon AI" in data["answer"]
    assert "hackathon" in data["answer"].lower()
    assert data["intent"] == "capability"

@pytest.mark.asyncio
async def test_assistant_unrelated_query(client):
    """Verify out-of-scope queries politely explain the assistant's boundaries."""
    res = await client.post("/api/v1/assistant/query", json={"query": "Write a python script to reverse a binary tree"})
    assert res.status_code == 200
    data = res.json()
    assert "specialize" in data["answer"].lower() or "tech event discovery" in data["answer"].lower()
    assert data["intent"] == "unrelated"
    assert len(data["events"]) == 0

@pytest.mark.asyncio
async def test_assistant_grounded_event_search(client):
    """Verify assistant retrieves actual database events with official registration links."""
    res = await client.post("/api/v1/assistant/query", json={"query": "Find AI hackathons in Telangana"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["events"]) >= 1
    first_ev = data["events"][0]
    assert "telangana" in (first_ev["state"] or "").lower() or first_ev["city"] == "Hyderabad"
    assert first_ev["registration_url"] or first_ev["official_website"]
    assert first_ev["verification_status"] == "verified"

@pytest.mark.asyncio
async def test_assistant_conversation_memory_followup(client):
    """Verify assistant retains context across follow-up queries."""
    # First turn
    turn1 = await client.post("/api/v1/assistant/query", json={"query": "Find AI hackathons in Telangana"})
    assert turn1.status_code == 200
    turn1_data = turn1.json()

    # Second turn: user asks follow-up about cost
    msgs = [
        {"role": "user", "content": "Find AI hackathons in Telangana"},
        {"role": "assistant", "content": turn1_data["answer"]}
    ]
    turn2 = await client.post("/api/v1/assistant/query", json={
        "query": "Are any of them free?",
        "messages": msgs
    })
    assert turn2.status_code == 200
    turn2_data = turn2.json()
    assert len(turn2_data["events"]) >= 1
    for ev in turn2_data["events"]:
        assert ev["is_free"] is True

@pytest.mark.asyncio
async def test_date_preset_filtering(client):
    """Verify events endpoint filters by date presets."""
    res_month = await client.get("/api/v1/events", params={"date_preset": "next_90_days"})
    assert res_month.status_code == 200
    data = res_month.json()
    assert "items" in data
    assert data["total"] >= 1

@pytest.mark.asyncio
async def test_event_not_found_404(client):
    """Verify missing event identifier returns clean 404."""
    res = await client.get("/api/v1/events/non-existent-event-slug-99999")
    assert res.status_code == 404
    assert "detail" in res.json()

@pytest.mark.asyncio
async def test_saved_events_persistence_flow(client):
    """Verify authenticated user can bookmark, list, and remove saved events."""
    # Register & login user
    user_email = "bookmark_user@example.com"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": user_email,
        "password": "Password123!",
        "full_name": "Bookmark Tester"
    })
    assert reg_resp.status_code == 200
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch an event to bookmark
    ev_resp = await client.get("/api/v1/events", params={"page_size": 1})
    event_id = ev_resp.json()["items"][0]["id"]

    # Save event
    save_resp = await client.post("/api/v1/auth/saved-events", json={"event_id": event_id}, headers=headers)
    assert save_resp.status_code == 200

    # List saved events
    list_saved = await client.get("/api/v1/auth/saved-events", headers=headers)
    assert list_saved.status_code == 200
    saved_ids = [item["event_id"] for item in list_saved.json()]
    assert event_id in saved_ids

    # Unsave event
    unsave_resp = await client.delete(f"/api/v1/auth/saved-events/{event_id}", headers=headers)
    assert unsave_resp.status_code == 200

    # Verify removed
    list_saved_after = await client.get("/api/v1/auth/saved-events", headers=headers)
    assert event_id not in [item["event_id"] for item in list_saved_after.json()]

@pytest.mark.asyncio
async def test_invalid_inputs_and_validation_errors(client):
    """Verify malformed requests return clean 4xx responses without 500 crashes."""
    # Empty query body for assistant
    res1 = await client.post("/api/v1/assistant/query", json={})
    assert res1.status_code == 422

    # Negative page size
    res2 = await client.get("/api/v1/events", params={"page": -1, "page_size": -5})
    assert res2.status_code == 422

    # Invalid event report on non-existent event
    res3 = await client.post("/api/v1/events/999999/report", json={
        "issue_type": "broken_link",
        "description": "testing 404 report"
    })
    assert res3.status_code == 404

@pytest.mark.asyncio
async def test_assistant_gemini_failure_fallback(client):
    """Verify that if external AI provider raises an error or times out, the assistant gracefully falls back."""
    with patch("backend.app.services.assistant_service.generate_gemini_conversational_response", side_effect=Exception("API timeout")):
        with patch("backend.app.core.config.settings.AI_API_KEY", "mock-test-key"):
            res = await client.post("/api/v1/assistant/query", json={"query": "Find AI hackathons in Telangana"})
            assert res.status_code == 200
            data = res.json()
            assert len(data["events"]) >= 1
            assert "Telangana" in data["events"][0]["title"] or "Telangana" in (data["events"][0]["state"] or "")
            assert "verified" in data["disclaimer"].lower() or "grounded" in data["disclaimer"].lower()
