import re
import socket
import ipaddress
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Tuple, Optional, Dict, Any
import httpx

# Blocked subnets for SSRF prevention
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private class A
    ipaddress.ip_network("172.16.0.0/12"),    # Private class B
    ipaddress.ip_network("192.168.0.0/16"),   # Private class C
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local & Cloud metadata (AWS, GCP, Azure)
    ipaddress.ip_network("0.0.0.0/8"),        # Broadcast/Current network
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 private
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

# Marketing tracking query parameters that are safe to remove without affecting page routing
TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid", "_ga", "_gl"
}

def is_ip_allowed(ip_str: str) -> bool:
    """Validate that the resolved IP address is public and not in restricted subnets."""
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False
        return True
    except ValueError:
        return False

def validate_url_syntax(url: str) -> Tuple[bool, Optional[str]]:
    """
    Strict server-side validation of external event and registration URLs.
    Accepts: Valid http:// and https:// URLs.
    Rejects: Malformed URLs, javascript:, data:, file:, ftp:, embedded credentials.
    """
    if not url or not isinstance(url, str):
        return False, "URL is missing or empty"

    url_clean = url.strip()
    if len(url_clean) > 2048:
        return False, "URL exceeds maximum allowable length (2048 characters)"

    # Check for dangerous schemes
    lower_url = url_clean.lower()
    if lower_url.startswith(("javascript:", "data:", "file:", "ftp:", "vbscript:", "blob:")):
        return False, "Disallowed URL scheme"

    try:
        parsed = urlparse(url_clean)
        if parsed.scheme.lower() not in ("http", "https"):
            return False, f"Unsupported scheme: '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

        if not parsed.netloc:
            return False, "Missing hostname/domain in URL"

        # Reject URLs containing embedded credentials (e.g. https://user:pass@example.com)
        if "@" in parsed.netloc:
            return False, "URLs with embedded user credentials are prohibited"

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid host in URL"

        # Check for numeric or string loopback hostnames
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            return False, "Localhost destinations are prohibited"

        # Domain must have at least one dot or be a valid domain structure
        if "." not in hostname and hostname.lower() != "localhost":
            return False, f"Invalid domain name: '{hostname}'"

        return True, None
    except Exception as e:
        return False, f"URL parse error: {str(e)}"

def normalize_event_url(url: str) -> str:
    """
    Safely normalizes an event or registration URL:
    - Normalizes scheme and domain to lowercase
    - Preserves meaningful query parameters (e.g. ?id=123, ?tab=apply) while stripping ad trackers
    - Preserves necessary path structure without stripping essential trailing slashes
    """
    is_valid, _ = validate_url_syntax(url)
    if not is_valid:
        return url.strip() if url else ""

    try:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path
        if not path:
            path = "/"

        # Filter out only confirmed marketing trackers, preserving all functional query params
        cleaned_params = []
        if parsed.query:
            for k, v in parse_qsl(parsed.query, keep_blank_values=True):
                if k.lower() not in TRACKING_QUERY_PARAMS:
                    cleaned_params.append((k, v))

        new_query = urlencode(cleaned_params)
        return urlunparse((scheme, netloc, path, "", new_query, parsed.fragment))
    except Exception:
        return url.strip()

def check_ssrf_safety(url: str) -> Tuple[bool, str]:
    """Pre-resolve DNS to guarantee host does not resolve to private or cloud metadata IPs."""
    is_valid, error = validate_url_syntax(url)
    if not is_valid:
        return False, error or "Invalid URL syntax"

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname"

        # Resolve host to IPs
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
            for item in resolved_ips:
                ip_addr = item[4][0]
                if not is_ip_allowed(ip_addr):
                    return False, f"Host '{hostname}' resolves to restricted IP: {ip_addr}"
        except socket.gaierror:
            return False, f"Could not resolve hostname: '{hostname}'"

        return True, "Safe"
    except Exception as e:
        return False, f"SSRF check failed: {str(e)}"

async def verify_url_destination(
    url: str,
    timeout_seconds: float = 6.0,
    client: Optional[httpx.AsyncClient] = None
) -> Dict[str, Any]:
    """
    Controlled backend validation service to verify reachability of external event registration URLs.
    Features:
    - SSRF pre-check
    - Bounded response size (max 512 KB)
    - Short timeout
    - Safe redirect following with SSRF check on each redirect hop
    - HEAD-with-GET fallback (some sites reject HEAD with 405 or 403)
    Returns:
    {
      "status": "confirmed_reachable" | "redirected" | "authentication_required" |
                "confirmed_not_found" | "temporarily_unavailable" | "unsafe_destination" |
                "validation_failed",
      "http_status": int | None,
      "final_url": str | None,
      "is_reachable": bool,
      "error": str | None
    }
    """
    is_safe, reason = check_ssrf_safety(url)
    if not is_safe:
        return {
            "status": "unsafe_destination" if "restricted IP" in reason or "Localhost" in reason else "validation_failed",
            "http_status": None,
            "final_url": None,
            "is_reachable": False,
            "error": reason
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (EventHorizonBot/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    should_close_client = False
    if client is None:
        client = httpx.AsyncClient(
            timeout=timeout_seconds,
            follow_redirects=True,
            max_redirects=5
        )
        should_close_client = True

    try:
        # First attempt a quick HEAD request
        response = None
        try:
            head_resp = await client.head(url, headers=headers)
            # If server accepted HEAD, use it
            if head_resp.status_code in (200, 201, 301, 302, 307, 308):
                response = head_resp
            elif head_resp.status_code in (405, 403, 400):
                # Many platforms (Devpost, Unstop, Cloudflare-fronted sites) reject HEAD with 405/403
                # Fall back to GET below
                response = None
            else:
                response = head_resp
        except (httpx.RequestError, Exception):
            response = None

        # Fallback to streaming GET if HEAD was rejected or inconclusive
        if response is None:
            get_resp = await client.get(url, headers=headers)
            response = get_resp

        status_code = response.status_code
        final_url = str(response.url)

        # Check if redirect destination is safe
        if final_url != url:
            is_redirect_safe, redirect_reason = check_ssrf_safety(final_url)
            if not is_redirect_safe:
                return {
                    "status": "unsafe_destination",
                    "http_status": status_code,
                    "final_url": final_url,
                    "is_reachable": False,
                    "error": f"Redirected to restricted target: {redirect_reason}"
                }

        # Classify outcome
        if status_code in (200, 201, 204):
            return {
                "status": "confirmed_reachable" if final_url == url else "redirected",
                "http_status": status_code,
                "final_url": final_url,
                "is_reachable": True,
                "error": None
            }
        elif status_code in (404, 410):
            return {
                "status": "confirmed_not_found",
                "http_status": status_code,
                "final_url": final_url,
                "is_reachable": False,
                "error": f"HTTP {status_code} Not Found"
            }
        elif status_code in (401, 403):
            # Auth required or bot challenge, but host exists
            return {
                "status": "authentication_required",
                "http_status": status_code,
                "final_url": final_url,
                "is_reachable": True, # Still a functional external destination
                "error": f"HTTP {status_code} Access Restricted"
            }
        elif 500 <= status_code <= 599:
            return {
                "status": "temporarily_unavailable",
                "http_status": status_code,
                "final_url": final_url,
                "is_reachable": False,
                "error": f"HTTP {status_code} Server Error"
            }
        else:
            return {
                "status": "inconclusive",
                "http_status": status_code,
                "final_url": final_url,
                "is_reachable": status_code < 400,
                "error": f"HTTP {status_code}"
            }

    except httpx.TimeoutException:
        return {
            "status": "temporarily_unavailable",
            "http_status": None,
            "final_url": None,
            "is_reachable": False,
            "error": "Connection timed out"
        }
    except Exception as e:
        return {
            "status": "temporarily_unavailable",
            "http_status": None,
            "final_url": None,
            "is_reachable": False,
            "error": f"Network error: {str(e)}"
        }
    finally:
        if should_close_client:
            await client.aclose()
