import pytest
from backend.app.discovery.fetcher import check_ssrf_safety, is_ip_allowed

def test_blocked_private_subnets():
    assert is_ip_allowed("127.0.0.1") is False
    assert is_ip_allowed("10.0.0.1") is False
    assert is_ip_allowed("172.16.0.5") is False
    assert is_ip_allowed("192.168.1.1") is False
    assert is_ip_allowed("169.254.169.254") is False # AWS metadata endpoint
    assert is_ip_allowed("8.8.8.8") is True          # Public Google DNS

def test_ssrf_url_guard():
    safe_localhost, _ = check_ssrf_safety("http://localhost:8000/internal")
    assert safe_localhost is False

    safe_loopback, _ = check_ssrf_safety("http://127.0.0.1:5000/admin")
    assert safe_loopback is False

    safe_file, _ = check_ssrf_safety("file:///etc/passwd")
    assert safe_file is False

    safe_public, _ = check_ssrf_safety("https://github.com/events")
    assert safe_public is True
