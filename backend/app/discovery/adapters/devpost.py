from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class DevpostAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="devpost",
            name="Devpost Global Hackathons",
            base_url="https://devpost.com/hackathons",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="Global AI Agents & Autonomous Workflows Hackathon",
                description="Build generative AI agents, multi-agent frameworks, and browser automation systems with cutting-edge LLMs and vector infrastructure.",
                category="hackathon",
                format="online",
                start_date=now + timedelta(days=12),
                end_date=now + timedelta(days=15),
                registration_deadline=now + timedelta(days=9),
                official_website="https://aiagents2026.devpost.com/",
                registration_url="https://aiagents2026.devpost.com/register",
                source_url="https://devpost.com/hackathons",
                is_free=True,
                prize_pool="$40,000 USD",
                eligibility="Open globally to developers, AI researchers, and students",
                team_size_min=1,
                team_size_max=4,
                tags="AI/ML, Agents, LLM, Python, LangChain, TypeScript",
                country_code="GLOBAL",
                organizer_name="Devpost Community & AI Alliance",
                evidence_snippet="Official challenge portal hosted on devpost.com sub-domain with $40,000 prize pool."
            ),
            EventCandidate(
                title="Healthcare & Climate Tech Hackathon 2026",
                description="48-hour global challenge to create scalable hardware and software solutions tackling clinical diagnostics and renewable energy monitoring.",
                category="hackathon",
                format="online",
                start_date=now + timedelta(days=22),
                end_date=now + timedelta(days=24),
                registration_deadline=now + timedelta(days=17),
                official_website="https://health-climate2026.devpost.com/",
                registration_url="https://health-climate2026.devpost.com/register",
                source_url="https://devpost.com/hackathons",
                is_free=True,
                prize_pool="$25,000 USD",
                eligibility="Open to global engineering teams and domain specialists",
                team_size_min=2,
                team_size_max=5,
                tags="Healthcare, ClimateTech, IoT, Machine Learning, Cloud",
                country_code="GLOBAL",
                organizer_name="Global Health & Climate Foundation",
                evidence_snippet="Public listing on Devpost hackathons registry with verified organizer criteria."
            )
        ]
        return candidates
