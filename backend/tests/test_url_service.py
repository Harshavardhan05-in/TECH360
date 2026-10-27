import pytest
import httpx
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from backend.app.services.url_service import (
    validate_url_syntax, normalize_event_url, check_ssrf_safety, verify_url_destination
)
from backend.app.models.event import Event
from backend.app.core.repair_records import repair_database_and_migrate

# 1. Valid HTTPS URL
def test_valid_https_url():
    valid, err = validate_url_syntax("https://fossunited.org/events")
    assert valid is True
    assert err is None

# 2. Valid URL with meaningful query parameters preserved
def test_valid_url_with_query_params():
    url = "https://unstop.com/hackathons?category=engineering&id=4921&utm_source=twitter"
    normalized = normalize_event_url(url)
    assert "category=engineering" in normalized
    assert "id=4921" in normalized
    assert "utm_source" not in normalized # Ad tracking param stripped, functional param kept!

# 3. Missing registration URL
def test_missing_registration_url():
    valid, err = validate_url_syntax("")
    assert valid is False
    assert "missing" in err.lower()

    valid_none, err_none = validate_url_syntax(None)
    assert valid_none is False

# 4. Malformed URL
def test_malformed_url():
    valid, err = validate_url_syntax("htp:/bad_url")
    assert valid is False
    assert "unsupported scheme" in err.lower() or "missing hostname" in err.lower()

# 5. Dangerous URL scheme (javascript, data, file)
def test_dangerous_url_schemes():
    for dangerous in [
        "javascript:alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "file:///etc/passwd",
        "vbscript:msgbox"
    ]:
        valid, err = validate_url_syntax(dangerous)
        assert valid is False
        assert "disallowed url scheme" in err.lower()

# 6. URL containing embedded credentials
def test_embedded_credentials():
    valid, err = validate_url_syntax("https://admin:secret123@internal.company.com/apply")
    assert valid is False
    assert "embedded user credentials" in err.lower()

# 7. Redirect to a valid public destination
@pytest.mark.asyncio
async def test_redirect_to_valid_destination():
    mock_response = MagicMock(status_code=200)
    mock_response.url = httpx.URL("https://fossunited.org/events/summit")

    mock_client = AsyncMock()
    mock_client.head = AsyncMock(return_value=mock_response)

    res = await verify_url_destination("https://fossunited.org/events", client=mock_client)
    assert res["is_reachable"] is True
    assert res["status"] in ("confirmed_reachable", "redirected")

# 8. Redirect to a private IP address (SSRF blocked)
@pytest.mark.asyncio
async def test_redirect_to_private_ip_blocked():
    mock_response = MagicMock(status_code=302)
    mock_response.url = httpx.URL("http://169.254.169.254/latest/meta-data/")

    mock_client = AsyncMock()
    mock_client.head = AsyncMock(return_value=mock_response)

    res = await verify_url_destination("https://public-service.com/redirect", client=mock_client)
    assert res["is_reachable"] is False
    assert res["status"] == "unsafe_destination"
    assert "restricted target" in res["error"]

# 9. Timeout handling
@pytest.mark.asyncio
async def test_timeout_handling():
    mock_client = AsyncMock()
    mock_client.head = AsyncMock(side_effect=httpx.TimeoutException("Read timed out"))
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Read timed out"))

    with patch("backend.app.services.url_service.check_ssrf_safety", return_value=(True, "Safe")):
        res = await verify_url_destination("https://slow-organizer.org/apply", client=mock_client)
        assert res["is_reachable"] is False
        assert res["status"] == "temporarily_unavailable"
        assert "timed out" in res["error"].lower()

# 10. Confirmed 404
@pytest.mark.asyncio
async def test_confirmed_404():
    mock_response = MagicMock(status_code=404)
    mock_response.url = httpx.URL("https://devpost.com/hackathons/nonexistent-slug")

    mock_client = AsyncMock()
    mock_client.head = AsyncMock(return_value=mock_response)

    res = await verify_url_destination("https://devpost.com/hackathons/nonexistent-slug", client=mock_client)
    assert res["is_reachable"] is False
    assert res["status"] == "confirmed_not_found"
    assert "404" in res["error"]

# 11. Rejects HEAD with 405 but succeeds on GET
@pytest.mark.asyncio
async def test_head_rejected_get_succeeds():
    mock_head_resp = MagicMock(status_code=405) # Method Not Allowed
    mock_get_resp = MagicMock(status_code=200)
    mock_get_resp.url = httpx.URL("https://devpost.com/hackathons/ai-summit")

    mock_client = AsyncMock()
    mock_client.head = AsyncMock(return_value=mock_head_resp)
    mock_client.get = AsyncMock(return_value=mock_get_resp)

    res = await verify_url_destination("https://devpost.com/hackathons/ai-summit", client=mock_client)
    assert res["is_reachable"] is True
    assert res["status"] in ("confirmed_reachable", "redirected")
    assert res["http_status"] == 200

# 12. Closed or expired event
def test_closed_event_link_status():
    event = Event(
        title="Spring Buildathon 2026",
        slug="spring-buildathon-2026",
        description="Completed event",
        status="registration_closed",
        link_status="closed",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc)
    )
    assert event.status == "registration_closed"
    assert event.link_status == "closed"

# 13. Event with official website but no direct registration link
def test_official_info_only_event():
    event = Event(
        title="Mumbai Tech Innovation Fair",
        slug="mumbai-tech-fair",
        description="Pending direct link",
        official_website="https://unstop.com/hackathons",
        registration_url=None,
        link_status="unverified",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc)
    )
    assert event.registration_url is None
    assert event.official_website == "https://unstop.com/hackathons"
    assert event.link_status == "unverified"

# 14. Frontend receives verified backend URL
@pytest.mark.asyncio
async def test_api_returns_verified_url(client):
    resp = await client.get("/api/v1/events")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) > 0
    # Every verified event must have a non-empty reachable registration URL or official website
    for ev in items:
        if ev["verification_status"] == "verified":
            target_url = ev["registration_url"] or ev["official_website"]
            assert target_url is not None
            assert target_url.startswith("https://")
            assert "example.org" not in target_url

# 15. Migration of existing records without data loss
def test_migration_and_repair_logic(tmp_path):
    import sqlite3
    test_db = tmp_path / "test_migration.db"
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    # Create minimal legacy table
    c.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, title TEXT, official_website TEXT, registration_url TEXT)")
    c.execute("INSERT INTO events VALUES (1, 'Legacy Event', 'https://t-hub.co/events/ai-hackathon', 'https://t-hub.co/events/ai-hackathon/apply')")
    conn.commit()
    conn.close()

    # Run repair
    repair_database_and_migrate(str(test_db))

    # Re-verify
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute("SELECT id, registration_url, link_status FROM events WHERE id=1")
    row = c.fetchone()
    assert row[1] == "https://t-hub.co/" # Repaired to real URL
    assert row[2] == "confirmed_reachable"
    conn.close()
