import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.app.models.event import Event
from backend.app.models.observation import EventSourceObservation

TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "reference", "fbclid", "gclid", "msclkid", "mc_cid", "mc_eid"
}

def canonicalize_url(raw_url: str) -> str:
    """
    Standardize a URL by lowercasing scheme/host, stripping trailing slashes,
    and removing marketing tracking query parameters.
    """
    if not raw_url:
        return ""
    try:
        parsed = urlparse(raw_url.strip())
        # Clean scheme & netloc
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        
        # Clean path
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # Filter query params
        cleaned_query_params = []
        if parsed.query:
            for k, v in parse_qsl(parsed.query, keep_blank_values=False):
                if k.lower() not in TRACKING_QUERY_PARAMS:
                    cleaned_query_params.append((k, v))
        
        # Sort query params deterministically
        cleaned_query_params.sort(key=lambda x: x[0])
        new_query = urlencode(cleaned_query_params)

        return urlunparse((scheme, netloc, path, "", new_query, ""))
    except Exception:
        return raw_url.strip()

def tokenize_title(title: str) -> set:
    """Normalize and tokenize an event title into unique lowercase alphanumeric terms."""
    clean = re.sub(r"[^\w\s]", " ", title.lower())
    stop_words = {"the", "and", "for", "with", "hackathon", "summit", "conference", "fest", "expo"}
    tokens = {t for t in clean.split() if len(t) >= 2 and t not in stop_words}
    return tokens

def compute_title_similarity(title_a: str, title_b: str) -> float:
    """Compute Jaccard token overlap between two event titles."""
    tokens_a = tokenize_title(title_a)
    tokens_b = tokenize_title(title_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / len(union)

async def find_duplicate_candidate(
    db: AsyncSession,
    canonical_url: str,
    title: str,
    start_date = None
) -> Tuple[Optional[Event], str, float]:
    """
    Check if a candidate event already exists via:
    1. Exact canonical URL match in existing observations (confidence: 1.0)
    2. High title similarity (>= 0.75) within date range (confidence: similarity score)
    Returns: (matching_event, match_reason, confidence)
    """
    # 1. Exact Canonical URL match in observations
    if canonical_url:
        obs_stmt = select(EventSourceObservation).where(EventSourceObservation.canonical_url == canonical_url)
        obs_res = await db.execute(obs_stmt)
        matched_obs = obs_res.scalar_one_or_none()
        if matched_obs and matched_obs.event_id:
            event_res = await db.execute(select(Event).where(Event.id == matched_obs.event_id))
            ev = event_res.scalar_one_or_none()
            if ev:
                return ev, "EXACT_CANONICAL_URL_MATCH", 1.0

    # 2. Check title similarity against upcoming/recent events
    candidates_stmt = select(Event).limit(200)
    candidates_res = await db.execute(candidates_stmt)
    candidates = candidates_res.scalars().all()

    best_match = None
    best_score = 0.0

    for cand in candidates:
        sim = compute_title_similarity(title, cand.title)
        if sim > best_score:
            best_score = sim
            best_match = cand

    if best_score >= 0.75 and best_match:
        return best_match, "FUZZY_TITLE_OVERLAP", best_score

    return None, "NO_DUPLICATE_FOUND", 0.0
