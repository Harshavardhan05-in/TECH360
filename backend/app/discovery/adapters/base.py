import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger("eventhorizon.discovery")

class EventCandidate:
    """Standardized event candidate discovered by an adapter."""
    def __init__(
        self,
        title: str,
        description: str,
        category: str,
        format: str,
        start_date: datetime,
        end_date: datetime,
        registration_deadline: Optional[datetime] = None,
        official_website: Optional[str] = None,
        registration_url: Optional[str] = None,
        source_url: Optional[str] = None,
        is_free: bool = True,
        prize_pool: Optional[str] = None,
        fee_details: Optional[str] = None,
        eligibility: Optional[str] = None,
        team_size_min: int = 1,
        team_size_max: int = 4,
        tags: Optional[str] = None,
        country_code: str = "IN",
        state_slug: Optional[str] = None,
        city: Optional[str] = None,
        venue_name: Optional[str] = None,
        venue_address: Optional[str] = None,
        organizer_name: Optional[str] = None,
        organizer_website: Optional[str] = None,
        evidence_snippet: Optional[str] = None,
        raw_payload: Optional[Dict[str, Any]] = None,
    ):
        self.title = title.strip()
        self.description = description.strip()
        self.category = category.lower()
        self.format = format.lower()
        self.start_date = start_date
        self.end_date = end_date
        self.registration_deadline = registration_deadline
        self.official_website = official_website
        self.registration_url = registration_url
        self.source_url = source_url
        self.is_free = is_free
        self.prize_pool = prize_pool
        self.fee_details = fee_details
        self.eligibility = eligibility
        self.team_size_min = team_size_min
        self.team_size_max = team_size_max
        self.tags = tags
        self.country_code = country_code
        self.state_slug = state_slug
        self.city = city
        self.venue_name = venue_name
        self.venue_address = venue_address
        self.organizer_name = organizer_name
        self.organizer_website = organizer_website
        self.evidence_snippet = evidence_snippet
        self.raw_payload = raw_payload or {}

class BaseDiscoveryAdapter(ABC):
    """Abstract base class for all event discovery source adapters."""

    def __init__(
        self,
        source_slug: str,
        name: str,
        base_url: str,
        rate_limit_per_min: int = 30,
        timeout_seconds: int = 15,
        max_retries: int = 3
    ):
        self.source_slug = source_slug
        self.name = name
        self.base_url = base_url
        self.rate_limit_per_min = rate_limit_per_min
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.delay_between_requests = 60.0 / max(1, rate_limit_per_min)

    @abstractmethod
    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        """Fetch and extract event candidates from the source."""
        pass

    async def sleep_with_jitter(self, base_delay: Optional[float] = None):
        """Throttle requests with exponential backoff and randomized jitter to respect server health."""
        delay = base_delay or self.delay_between_requests
        jitter = random.uniform(0.1, 0.4)
        await asyncio.sleep(delay + jitter)
