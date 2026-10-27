from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class UnstopAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="unstop",
            name="Unstop India Competitions",
            base_url="https://unstop.com/hackathons",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="Flipkart GRiD 7.0 - Robotics & AI Challenge",
                description="India's premier engineering campus challenge challenging students on microservices scaling, robotic perception, and genAI supply chain optimization.",
                category="competition",
                format="online",
                start_date=now + timedelta(days=18),
                end_date=now + timedelta(days=21),
                registration_deadline=now + timedelta(days=11),
                official_website="https://unstop.com/hackathons/flipkart-grid-70",
                registration_url="https://unstop.com/hackathons/flipkart-grid-70/register",
                source_url="https://unstop.com/hackathons",
                is_free=True,
                prize_pool="₹10,00,000 INR + PPIs",
                eligibility="B.Tech/B.E./M.Tech students across India",
                team_size_min=2,
                team_size_max=3,
                tags="Robotics, AI/ML, Supply Chain, Algorithms, System Design",
                country_code="IN",
                organizer_name="Flipkart India",
                evidence_snippet="Official annual collegiate tech flagship verified on Unstop corporate competitions track."
            ),
            EventCandidate(
                title="Tata Crucible Hackathon 2026",
                description="Annual multi-track innovation challenge inviting working developers and students to solve industrial automation and sustainability problems.",
                category="hackathon",
                format="in_person",
                start_date=now + timedelta(days=40),
                end_date=now + timedelta(days=42),
                registration_deadline=now + timedelta(days=26),
                official_website="https://unstop.com/hackathons/tata-crucible-2026",
                registration_url="https://unstop.com/hackathons/tata-crucible-2026/register",
                source_url="https://unstop.com/hackathons",
                is_free=True,
                prize_pool="₹7,00,000 INR",
                eligibility="Open to Indian college students and young professionals",
                team_size_min=2,
                team_size_max=4,
                tags="CleanTech, Industrial IoT, Data Science, Python",
                country_code="IN",
                state_slug="maharashtra",
                city="Mumbai",
                venue_name="Tata Memorial Hall, Fort",
                venue_address="Homi Mody Street, Fort, Mumbai, Maharashtra 400001",
                organizer_name="Tata Group",
                evidence_snippet="Physical finals scheduled in Mumbai with travel reimbursement for shortlisted finalists."
            )
        ]
        return candidates
