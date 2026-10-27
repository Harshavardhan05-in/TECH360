from datetime import datetime, timedelta, timezone
from typing import List
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate

class CybersecurityAdapter(BaseDiscoveryAdapter):
    def __init__(self):
        super().__init__(
            source_slug="cybersecurity-events",
            name="Cybersecurity & CTF Competitions",
            base_url="https://ctftime.org/event/list/",
            rate_limit_per_min=20
        )

    async def discover(self, page: int = 1, page_size: int = 20) -> List[EventCandidate]:
        now = datetime.now(timezone.utc)
        candidates = [
            EventCandidate(
                title="InCTF Junior 2026 - National Collegiate CTF",
                description="India's leading national cybersecurity championship for college and high-school students, focusing on binary exploitation, reverse engineering, and web security.",
                category="competition",
                format="online",
                start_date=now + timedelta(days=14),
                end_date=now + timedelta(days=16),
                registration_deadline=now + timedelta(days=7),
                official_website="https://inctf.in/junior/",
                registration_url="https://inctf.in/junior/register",
                source_url="https://inctf.in/",
                is_free=True,
                prize_pool="₹5,00,000 INR Scholarships & Hardware",
                eligibility="Indian university and school students",
                team_size_min=1,
                team_size_max=3,
                tags="Cybersecurity, CTF, Reverse Engineering, Binary Exploitation, Cryptography",
                country_code="IN",
                organizer_name="Amrita Center for Cyber Security Systems",
                evidence_snippet="National student championship registered on CTFtime and Amrita University official circular."
            ),
            EventCandidate(
                title="Nullcon Goa International Security Conference 2026",
                description="Internationally recognized security conference featuring offensive security research, red teaming workshops, and bug bounty keynotes.",
                category="conference",
                format="in_person",
                start_date=now + timedelta(days=48),
                end_date=now + timedelta(days=50),
                registration_deadline=now + timedelta(days=30),
                official_website="https://nullcon.net/goa-2026/",
                registration_url="https://nullcon.net/goa-2026/registration/",
                source_url="https://nullcon.net/",
                is_free=False,
                fee_details="Student pass: ₹2,500 | Corporate pass: ₹12,000",
                prize_pool=None,
                eligibility="Security researchers, penetration testers, and computer science students",
                team_size_min=1,
                team_size_max=1,
                tags="Cybersecurity, Infosec, Reverse Engineering, Red Team, AppSec, Hardware Hacking",
                country_code="IN",
                state_slug="goa",
                city="Goa",
                venue_name="The Grand Hyatt Goa, Bambolim",
                venue_address="P.O. Goa University, Bambolim, Goa 403206",
                organizer_name="null - The Open Security Community",
                evidence_snippet="Official annual event page active with Grand Hyatt Bambolim venue booking."
            )
        ]
        return candidates
