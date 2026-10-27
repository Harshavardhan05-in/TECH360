import pytest
from backend.app.services.search_service import parse_natural_language_search

@pytest.mark.asyncio
async def test_natural_language_query_parser():
    """Verify that the natural language query parser extracts structured filters from free-text queries."""
    
    # 1. AI hackathons in Telangana
    p1 = parse_natural_language_search("AI hackathons in Telangana")
    assert p1["category"] == "hackathon"
    assert p1["state_slug"] == "telangana"
    assert "ai" in p1["tokens"]
    
    # 2. Online cybersecurity competitions
    p2 = parse_natural_language_search("online cybersecurity competitions with registration still open")
    assert p2["format"] == "online"
    assert p2["category"] == "competition"
    assert p2["status"] in ("upcoming", "published")
    assert "cybersecurity" in p2["tokens"]
    
    # 3. Free Python workshops
    p3 = parse_natural_language_search("free Python workshops for college students")
    assert p3["is_free"] is True
    assert p3["category"] == "workshop"
    assert "python" in p3["tokens"]
    
    # 4. Hackathons with deadlines within 7 days
    p4 = parse_natural_language_search("hackathons with deadlines within 7 days")
    assert p4["category"] == "hackathon"
    assert p4["deadline_within_days"] == 7
    
    # 5. Beginner-friendly machine-learning workshops
    p5 = parse_natural_language_search("beginner-friendly machine-learning workshops")
    assert p5["category"] == "workshop"
    assert "machine" in p5["tokens"] or "learning" in p5["tokens"]
    
    # 6. Events in Karnataka that allow individual participation
    p6 = parse_natural_language_search("events in Karnataka that allow individual participation")
    assert p6["state_slug"] == "karnataka"
    assert p6["team_size_min"] == 1


@pytest.mark.asyncio
async def test_nl_search_api_execution(client):
    """Verify end-to-end API execution of natural-language search queries against seeded database."""
    
    # 1. Query AI hackathons in Telangana
    res1 = await client.get("/api/v1/events", params={"q": "AI hackathons in Telangana"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["total"] >= 1
    for ev in data1["items"]:
        assert ev["category"] == "hackathon"
        assert ev["region"]["slug"] == "telangana"
        assert "karnataka" not in ev["region"]["slug"]
        
    # 2. Query free Python workshops
    res2 = await client.get("/api/v1/events", params={"q": "free Python workshops"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["total"] >= 1
    for ev in data2["items"]:
        assert ev["is_free"] is True
        assert ev["category"] == "workshop"
        assert "python" in ev["title"].lower() or "python" in (ev["tags"] or "").lower() or "fastapi" in ev["title"].lower()

    # 3. Query events in Karnataka individual participation
    res3 = await client.get("/api/v1/events", params={"q": "events in Karnataka individual"})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["total"] >= 1
    for ev in data3["items"]:
        assert ev["region"]["slug"] == "karnataka"
        assert ev["team_size_min"] == 1

    # 4. Query hackathons with deadlines within 7 days
    res4 = await client.get("/api/v1/events", params={"q": "hackathons with deadlines within 7 days"})
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["total"] >= 1
    for ev in data4["items"]:
        assert ev["category"] == "hackathon"
        assert ev["registration_deadline"] is not None


@pytest.mark.asyncio
async def test_zero_result_fallback(client):
    """Verify searching for non-matching strings returns 200 OK with empty items list and no crashes."""
    res = await client.get("/api/v1/events", params={"q": "xyzcompletelynonexistenteventphrase9999"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_parse_query_endpoint(client):
    """Verify GET /api/v1/events/parse-query exposes the NLP query parsing logic to frontend."""
    res = await client.get("/api/v1/events/parse-query", params={"q": "AI hackathons in Telangana"})
    assert res.status_code == 200
    data = res.json()
    assert data["raw_query"] == "AI hackathons in Telangana"
    assert data["parsed"]["category"] == "hackathon"
    assert data["parsed"]["state_slug"] == "telangana"


@pytest.mark.asyncio
async def test_exact_registration_url_integrity(client):
    """Verify that all events have authentic, exact registration URLs rather than generic platform homepages."""
    res = await client.get("/api/v1/events", params={"page_size": 50})
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 20
    
    for ev in items:
        # Every event must have either an exact registration URL or official website
        reg_url = ev["registration_url"]
        web_url = ev["official_website"]
        assert reg_url or web_url, f"Event {ev['title']} missing both registration_url and official_website"
        
        # If registration_url is present, it must be an event-specific URL
        if reg_url:
            assert reg_url.startswith("https://") or reg_url.startswith("http://")
            # Should not be just a bare platform homepage like "https://mlh.io" without a path or subdomain
            forbidden_bare_roots = [
                "https://mlh.io", "https://mlh.io/",
                "https://devpost.com", "https://devpost.com/",
                "https://devfolio.co", "https://devfolio.co/",
                "https://unstop.com", "https://unstop.com/"
            ]
            assert reg_url not in forbidden_bare_roots, f"Event {ev['title']} has generic platform root URL: {reg_url}"


@pytest.mark.asyncio
async def test_cross_state_geo_leakage_with_expanded_dataset(client):
    """Verify rigorous geographic isolation across the expanded 20+ event dataset."""
    # Telangana
    res_tg = await client.get("/api/v1/events", params={"state_slug": "telangana"})
    assert res_tg.status_code == 200
    for ev in res_tg.json()["items"]:
        assert ev["region"]["slug"] == "telangana"
        assert ev["format"] != "online" or ev["city"] is not None
        
    # Karnataka
    res_ka = await client.get("/api/v1/events", params={"state_slug": "karnataka"})
    assert res_ka.status_code == 200
    for ev in res_ka.json()["items"]:
        assert ev["region"]["slug"] == "karnataka"

    # Maharashtra
    res_mh = await client.get("/api/v1/events", params={"state_slug": "maharashtra"})
    assert res_mh.status_code == 200
    for ev in res_mh.json()["items"]:
        assert ev["region"]["slug"] == "maharashtra"
