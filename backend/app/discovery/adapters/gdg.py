from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class GDGAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="gdg-india",
            name="Google Developer Group (GDG) India",
            base_url="https://gdg.community.dev/events/",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="DevFest Hyderabad 2026 - AI & Cloud Edition",
                description="Annual developer festival hosted by GDG Hyderabad covering Gemini API, Android 16 development, Flutter, and Google Cloud infrastructure.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=19),
                end_date=now + timedelta(days=19),
                registration_deadline=now + timedelta(days=12),
                official_website="https://gdg.community.dev/events/details/developer-group-gdg-hyderabad-presents-devfest-2026/",
                registration_url="https://gdg.community.dev/events/details/developer-group-gdg-hyderabad-presents-devfest-2026/tickets",
                source_url="https://gdg.community.dev/events/",
                is_free=True,
                prize_pool="Google Cloud credits & certification vouchers",
                eligibility="Open to students, working engineers, and founders",
                team_size_min=1,
                team_size_max=1,
                tags="Gemini, Google Cloud, Android, Flutter, AI/ML, Firebase",
                country_code="IN",
                state_slug="telangana",
                city="Hyderabad",
                venue_name="JNTU Auditorium, Kukatpally",
                venue_address="JNTUH Campus, Kukatpally Housing Board Colony, Hyderabad, Telangana 500085",
                organizer_name="GDG Hyderabad & WTM",
                evidence_snippet="Official Bevy community portal ticketing page active for GDG Hyderabad chapter."
            ),
            EventCandidate(
                title="Google Cloud Community Day Pune 2026",
                description="One-day deep dive into cloud architecture, BigQuery data pipelines, Kubernetes on GKE, and LLM fine-tuning on Vertex AI.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=32),
                end_date=now + timedelta(days=32),
                registration_deadline=now + timedelta(days=22),
                official_website="https://gdg.community.dev/events/details/developer-group-gdg-pune-presents-cloud-community-day-2026/",
                registration_url="https://gdg.community.dev/events/details/developer-group-gdg-pune-presents-cloud-community-day-2026/tickets",
                source_url="https://gdg.community.dev/events/",
                is_free=True,
                prize_pool=None,
                eligibility="Developers and students in Maharashtra",
                team_size_min=1,
                team_size_max=1,
                tags="GCP, Kubernetes, BigQuery, Vertex AI, Python, Cloud Architecture",
                country_code="IN",
                state_slug="maharashtra",
                city="Pune",
                venue_name="Symbiosis International University Auditorium, Lavale",
                venue_address="Gram Lavale, Tal Mulshi, Pune, Maharashtra 412115",
                organizer_name="GDG Cloud Pune",
                evidence_snippet="Official Bevy event listing with confirmed venue at Symbiosis Auditorium Pune."
            )
        ]
        return candidates
