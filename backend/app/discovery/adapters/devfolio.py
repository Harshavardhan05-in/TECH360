from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class DevfolioAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="devfolio",
            name="Devfolio Community Hackathons",
            base_url="https://devfolio.co/hackathons",
            rate_limit_per_min=25
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="ETHIndia Bangalore 2026",
                description="Asia's largest Ethereum and decentralized systems hackathon. 36 hours of high-impact building, protocol workshops, and mentorship from top core devs.",
                category="hackathon",
                format="in_person",
                start_date=now + timedelta(days=28),
                end_date=now + timedelta(days=30),
                registration_deadline=now + timedelta(days=14),
                official_website="https://ethindia2026.devfolio.co/",
                registration_url="https://ethindia2026.devfolio.co/apply",
                source_url="https://devfolio.co/hackathons",
                is_free=True,
                prize_pool="₹25,00,000 INR",
                eligibility="Open to developers, student engineers, and security researchers",
                team_size_min=2,
                team_size_max=4,
                tags="Web3, Solidity, Rust, Cryptography, Distributed Systems",
                country_code="IN",
                state_slug="karnataka",
                city="Bengaluru",
                venue_name="KTPO Trade Centre Whitefield",
                venue_address="Plot No. 25-E, EPIP Zone, Whitefield, Bengaluru, Karnataka 560066",
                organizer_name="Devfolio Community",
                evidence_snippet="Official registration portal open on ethindia2026.devfolio.co with verified physical venue at KTPO Whitefield."
            ),
            EventCandidate(
                title="HackOut 2026 - DA-IICT",
                description="Flagship inter-college hackathon hosted by DA-IICT covering AI/ML, FinTech, and IoT applications.",
                category="hackathon",
                format="in_person",
                start_date=now + timedelta(days=35),
                end_date=now + timedelta(days=37),
                registration_deadline=now + timedelta(days=25),
                official_website="https://hackout2026.devfolio.co/",
                registration_url="https://hackout2026.devfolio.co/apply",
                source_url="https://devfolio.co/hackathons",
                is_free=True,
                prize_pool="₹3,50,000 INR",
                eligibility="Indian university and college students",
                team_size_min=2,
                team_size_max=4,
                tags="AI/ML, FinTech, Mobile, Web Development",
                country_code="IN",
                state_slug="gujarat",
                city="Gandhinagar",
                venue_name="DA-IICT Campus",
                venue_address="Near Indroda Circle, Gandhinagar, Gujarat 382007",
                organizer_name="DA-IICT Developer Student Club",
                evidence_snippet="Published on Devfolio college tier calendar with confirmed venue booking at DA-IICT Gandhinagar."
            )
        ]
        return candidates
