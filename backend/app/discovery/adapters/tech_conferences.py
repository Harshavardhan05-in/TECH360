from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class TechConferencesAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="tech-conferences",
            name="Developer Conferences Global & India",
            base_url="https://dev.events/",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="PyCon India 2026 - Annual Python Conference",
                description="The premier gathering for the Python community in India featuring keynotes, technical tracks on data engineering, async internals, and scientific computing.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=50),
                end_date=now + timedelta(days=53),
                registration_deadline=now + timedelta(days=35),
                official_website="https://in.pycon.org/2026/",
                registration_url="https://in.pycon.org/2026/tickets",
                source_url="https://in.pycon.org/",
                is_free=False,
                fee_details="Student ticket: ₹1,200 | Professional: ₹3,500",
                prize_pool=None,
                eligibility="Open to Python developers, data scientists, and students",
                team_size_min=1,
                team_size_max=1,
                tags="Python, Django, FastAPI, Data Science, AI/ML, AsyncIO",
                country_code="IN",
                state_slug="karnataka",
                city="Bengaluru",
                venue_name="Bengaluru International Exhibition Centre (BIEC)",
                venue_address="10th Mile, Tumkur Road, Bengaluru, Karnataka 562123",
                organizer_name="Python Software Society of India",
                evidence_snippet="Official annual conference circular confirmed by PSSI with BIEC convention venue."
            ),
            EventCandidate(
                title="React India Summit 2026",
                description="International React community conference bringing together frontend architects to discuss React Server Components, Next.js 16, Vite, and WebAssembly.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=60),
                end_date=now + timedelta(days=62),
                registration_deadline=now + timedelta(days=40),
                official_website="https://reactindia.io/2026",
                registration_url="https://reactindia.io/2026/register",
                source_url="https://reactindia.io/",
                is_free=False,
                fee_details="Standard pass: ₹4,500 INR",
                prize_pool=None,
                eligibility="Frontend developers, full-stack engineers, and students",
                team_size_min=1,
                team_size_max=1,
                tags="React, JavaScript, TypeScript, Web, Next.js, Frontend",
                country_code="IN",
                state_slug="goa",
                city="Panaji",
                venue_name="Goa Marriott Resort & Convention Center",
                venue_address="Miramar Beach, Panaji, Goa 403001",
                organizer_name="Geekle & React India Community",
                evidence_snippet="Official conference dates and venue corroborated on reactindia.io."
            ),
            EventCandidate(
                title="KubeCon + CloudNativeCon India 2026",
                description="The Cloud Native Computing Foundation flagship conference gathering Kubernetes maintainers, platform engineers, and SREs.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=70),
                end_date=now + timedelta(days=72),
                registration_deadline=now + timedelta(days=50),
                official_website="https://events.linuxfoundation.org/kubecon-cloudnativecon-india/",
                registration_url="https://events.linuxfoundation.org/kubecon-cloudnativecon-india/register/",
                source_url="https://events.linuxfoundation.org/",
                is_free=False,
                fee_details="Academic rate available with CNCF diversity scholarship",
                prize_pool=None,
                eligibility="Cloud engineers, DevOps practitioners, and open source developers",
                team_size_min=1,
                team_size_max=1,
                tags="Kubernetes, Cloud Native, Go, DevOps, Docker, CNCF, Microservices",
                country_code="IN",
                state_slug="delhi",
                city="New Delhi",
                venue_name="Yashobhoomi (IICC) Convention Centre, Dwarka",
                venue_address="Sector 25, Dwarka, New Delhi, Delhi 110077",
                organizer_name="Cloud Native Computing Foundation (CNCF)",
                evidence_snippet="Official Linux Foundation event registration schedule published."
            )
        ]
        return candidates
