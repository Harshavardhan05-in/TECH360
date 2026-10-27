import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional, Tuple
import httpx

from backend.app.core.config import settings

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local & AWS/Cloud metadata
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

def is_ip_allowed(ip_str: str) -> bool:
    """Validate that the resolved IP address is public and does not belong to reserved subnets."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False
        return True
    except ValueError:
        return False

def check_ssrf_safety(url: str) -> Tuple[bool, str]:
    """
    Validates a URL before making an outbound request:
    - Only allows HTTP and HTTPS
    - Resolves host DNS and verifies the IP is public
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False, f"Unsupported scheme: {parsed.scheme}"
        
        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL"

        # Check for numeric loopbacks or internal localhost
        if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
            return False, "Access to localhost is prohibited"

        # Resolve host to IP
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
            for item in resolved_ips:
                ip_addr = item[4][0]
                if not is_ip_allowed(ip_addr):
                    return False, f"Resolved IP {ip_addr} is in a restricted network"
        except socket.gaierror:
            return False, "Could not resolve hostname"

        return True, "Safe"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

async def safe_fetch_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch a remote web page with SSRF protection, strict timeouts, and payload size bounds.
    Returns: (html_content, error_message)
    """
    if settings.SSRF_PROTECTION_ENABLED:
        is_safe, reason = check_ssrf_safety(url)
        if not is_safe:
            return None, f"SSRF Block: {reason}"

    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(timeout=settings.CRAWLER_TIMEOUT_SECONDS, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None, f"HTTP {resp.status_code}"

            # Limit payload size
            content = resp.text
            if len(content.encode("utf-8")) > settings.CRAWLER_MAX_CONTENT_BYTES:
                content = content[:settings.CRAWLER_MAX_CONTENT_BYTES]

            return content, None
    except httpx.TimeoutException:
        return None, "Request timed out"
    except Exception as e:
        return None, f"Fetch error: {str(e)}"
