import pytest

@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["database"]["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "EventHorizon AI"

@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
