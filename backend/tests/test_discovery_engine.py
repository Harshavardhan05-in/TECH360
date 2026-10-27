import pytest
from datetime import datetime, timezone, timedelta
from backend.app.discovery.adapters import (
    ADAPTER_REGISTRY,
    get_adapter_for_source,
    get_all_adapters,
    BaseDiscoveryAdapter,
    EventCandidate
)
from backend.app.discovery.engine import DiscoveryEngine
from backend.app.discovery.scheduler import DiscoveryScheduler
from backend.app.models.source import SourceRegistry
from backend.app.models.observation import EventSourceObservation
from backend.app.main import seed_default_sources
from sqlalchemy import select

def test_discovery_adapter_registry():
    """Verify that all discovery source adapters are correctly registered and inherit from BaseDiscoveryAdapter."""
    adapters = get_all_adapters()
    assert len(adapters) >= 7
    
    expected_slugs = [
        "devpost",
        "devfolio",
        "unstop",
        "foss-united",
        "tech-conferences",
        "gdg-india",
        "cybersecurity-events"
    ]
    
    for slug in expected_slugs:
        assert slug in ADAPTER_REGISTRY, f"Missing expected adapter: {slug}"
        adapter = get_adapter_for_source(slug)
        assert isinstance(adapter, BaseDiscoveryAdapter)
        assert adapter.timeout_seconds > 0
        assert adapter.source_slug == slug


@pytest.mark.asyncio
async def test_adapter_candidate_validation():
    """Verify that EventCandidate enforces required event fields and types."""
    now = datetime.now(timezone.utc)
    
    cand = EventCandidate(
        title="Test Buildathon 2026",
        description="A great developer hackathon.",
        category="hackathon",
        format="in_person",
        start_date=now,
        end_date=now + timedelta(days=2),
        city="Hyderabad",
        state_slug="telangana",
        registration_url="https://example.com/apply-2026",
        source_url="https://example.com/events/1"
    )
    assert cand.title == "Test Buildathon 2026"
    assert cand.state_slug == "telangana"
    assert cand.registration_url == "https://example.com/apply-2026"


@pytest.mark.asyncio
async def test_discovery_engine_execution_and_deduplication(db_session):
    """Verify that the discovery engine runs an adapter, persists new events, and logs crawl observations."""
    await seed_default_sources(db_session)
    
    # Run devpost adapter against test database
    res1 = await DiscoveryEngine.run_source_discovery(db_session, "devpost")
    assert res1["status"] == "success"
    assert res1["source"] == "devpost"
    
    # Verify crawl observations exist
    obs_res = await db_session.execute(select(EventSourceObservation))
    observations = obs_res.scalars().all()
    assert len(observations) >= 1
    
    # Running discovery a second time should detect duplicates
    res2 = await DiscoveryEngine.run_source_discovery(db_session, "devpost")
    assert res2["status"] == "success"
    assert res2["events_created"] == 0
    assert res2["duplicates_detected"] >= 1


@pytest.mark.asyncio
async def test_discovery_scheduler_lifecycle():
    """Verify that the background discovery scheduler can start and cancel cleanly without errors."""
    assert not DiscoveryScheduler._is_running
    
    DiscoveryScheduler.start(interval_seconds=3600)
    assert DiscoveryScheduler._is_running
    
    DiscoveryScheduler.stop()
    assert not DiscoveryScheduler._is_running


@pytest.mark.asyncio
async def test_admin_discovery_trigger_endpoint(client, db_session):
    """Verify that the admin discovery trigger endpoint responds correctly."""
    await seed_default_sources(db_session)

    # Register an admin user
    reg_payload = {
        "email": "ops-admin@eventhorizon.ai",
        "password": "SecurePassword123!",
        "full_name": "Operations Admin"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code in (200, 201)
    
    # Grant admin privilege in database
    from backend.app.models.user import User
    user_res = await db_session.execute(select(User).where(User.email == "ops-admin@eventhorizon.ai"))
    user = user_res.scalar_one()
    user.role = "admin"
    await db_session.commit()
    
    # Login as admin
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "ops-admin@eventhorizon.ai",
        "password": "SecurePassword123!"
    })
    token = login_res.json()["access_token"]
    
    # Trigger source discovery
    run_res = await client.post(
        "/api/v1/admin/discovery/sources/devfolio/run",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert run_res.status_code == 200
    data = run_res.json()
    assert data["source"] == "devfolio"
    assert data["status"] == "success"
    assert "events_created" in data
