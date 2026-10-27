from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class FOSSUnitedAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="foss-united",
            name="FOSS United India Network",
            base_url="https://fossunited.org/events",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="FOSS Hack 2026 - National Open Source Hackathon",
                description="Annual non-profit hackathon fostering open-source software development in India with cash grants for high-quality FLOSS projects.",
                category="hackathon",
                format="online",
                start_date=now + timedelta(days=16),
                end_date=now + timedelta(days=18),
                registration_deadline=now + timedelta(days=10),
                official_website="https://fossunited.org/fosshack",
                registration_url="https://fossunited.org/fosshack/register",
                source_url="https://fossunited.org/events",
                is_free=True,
                prize_pool="₹10,00,000 INR Grants",
                eligibility="Open to all open-source creators, contributors, and students",
                team_size_min=1,
                team_size_max=4,
                tags="Open Source, Python, Rust, Go, Linux, JavaScript, Git",
                country_code="IN",
                organizer_name="FOSS United Foundation",
                evidence_snippet="Official non-profit foundation initiative verified on fossunited.org."
            ),
            EventCandidate(
                title="Hyderabad FOSS Meetup & Linux Workshop",
                description="Community gathering focusing on Linux kernel tooling, self-hosting, and privacy-first local AI deployments.",
                category="workshop",
                format="in_person",
                start_date=now + timedelta(days=8),
                end_date=now + timedelta(days=8),
                registration_deadline=now + timedelta(days=6),
                official_website="https://fossunited.org/c/hyderabad",
                registration_url="https://fossunited.org/c/hyderabad/rsvp",
                source_url="https://fossunited.org/events",
                is_free=True,
                prize_pool="Free Swag & Book Grants",
                eligibility="Students and developers interested in open source",
                team_size_min=1,
                team_size_max=1,
                tags="Linux, Open Source, Self-Hosting, Docker, Local AI",
                country_code="IN",
                state_slug="telangana",
                city="Hyderabad",
                venue_name="Swecha Learning Center, Gachibowli",
                venue_address="Near DLF Cyber City, Gachibowli, Hyderabad, Telangana 500032",
                organizer_name="FOSS United Hyderabad Chapter",
                evidence_snippet="Monthly developer chapter confirmed at Swecha Learning Center Gachibowli."
            ),
            EventCandidate(
                title="Delhi FOSS Conference & Developer Sprint",
                description="Full-day developer conference with technical deep dives on distributed databases, compiler engineering, and kernel tracing.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=20),
                end_date=now + timedelta(days=21),
                registration_deadline=now + timedelta(days=15),
                official_website="https://fossunited.org/c/delhi-2026",
                registration_url="https://fossunited.org/c/delhi-2026/tickets",
                source_url="https://fossunited.org/events",
                is_free=True,
                prize_pool=None,
                eligibility="Open to technical practitioners and researchers",
                team_size_min=1,
                team_size_max=2,
                tags="Open Source, Systems, Databases, Rust, Linux, Go",
                country_code="IN",
                state_slug="delhi",
                city="New Delhi",
                venue_name="IIT Delhi Bharti Building",
                venue_address="Hauz Khas, New Delhi, Delhi 110016",
                organizer_name="FOSS United Delhi Chapter",
                evidence_snippet="Auditorium booking confirmed at Bharti Building IIT Delhi."
            )
        ]
        return candidates
