import pytest
from datetime import datetime, timedelta, timezone
from backend.app.services.verification_service import VerificationEngine
from backend.app.services.dedup_service import canonicalize_url, compute_title_similarity

def test_url_canonicalization():
    raw = "https://www.devpost.com/hackathons/ai-summit/?utm_source=twitter&utm_medium=social&ref=partner"
    clean = canonicalize_url(raw)
    assert "utm_source" not in clean
    assert "ref=" not in clean
    assert clean == "https://devpost.com/hackathons/ai-summit"

def test_title_similarity_computation():
    t1 = "Telangana AI & DeepTech Hackathon 2026"
    t2 = "Telangana AI DeepTech Hackathon"
    sim = compute_title_similarity(t1, t2)
    assert sim >= 0.75

    t3 = "Completely Unrelated Cyber Workshop"
    sim_low = compute_title_similarity(t1, t3)
    assert sim_low < 0.2

def test_verification_valid_event():
    now = datetime.now(timezone.utc)
    valid_event = {
        "registration_url": "https://devpost.com/hackathons/ai-event",
        "start_date": now + timedelta(days=10),
        "end_date": now + timedelta(days=12),
        "format": "online"
    }
    status, pos, warns = VerificationEngine.verify_event_data(valid_event)
    assert status == "verified"
    assert len(warns) == 0

def test_verification_invalid_dates():
    now = datetime.now(timezone.utc)
    invalid_event = {
        "registration_url": "https://devpost.com/hackathons/ai-event",
        "start_date": now + timedelta(days=10),
        "end_date": now + timedelta(days=5), # End before start!
        "format": "online"
    }
    status, pos, warns = VerificationEngine.verify_event_data(invalid_event)
    assert status == "needs_review"
    assert any("end date occurs before start date" in w for w in warns)
