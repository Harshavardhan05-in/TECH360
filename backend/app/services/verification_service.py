import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List
from urllib.parse import urlparse

class VerificationEngine:
    """
    Evidence-based multi-factor verification engine for technical events.
    Enforces deterministic validation rules before permitting publication.
    """

    TRUSTED_ORGANIZER_DOMAINS = {
        "mlh.io", "devpost.com", "unstop.com", "hackerearth.com", "eventbrite.com",
        "meetup.com", "github.com", "acm.org", "ieee.org", "gdg.community.dev"
    }

    @classmethod
    def verify_event_data(cls, event_data: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """
        Evaluates event data against verification rules.
        Returns: (status: 'verified' | 'unverified' | 'needs_review', positive_signals, warning_signals)
        """
        positive_signals = []
        warning_signals = []

        # 1. URL syntax and reachability heuristic
        reg_url = event_data.get("registration_url") or event_data.get("official_website")
        if not reg_url:
            warning_signals.append("Missing registration URL and official website")
        else:
            parsed = urlparse(reg_url)
            if not parsed.scheme or not parsed.netloc:
                warning_signals.append("Malformed registration or website URL")
            else:
                positive_signals.append("Valid registration URL structure")
                domain = parsed.netloc.lower()
                if any(domain.endswith(trusted) for trusted in cls.TRUSTED_ORGANIZER_DOMAINS):
                    positive_signals.append(f"Domain '{domain}' matches trusted tech organizer index")

        # 2. Date sanity check
        start_date = event_data.get("start_date")
        end_date = event_data.get("end_date")
        now = datetime.now(timezone.utc)

        if not start_date or not end_date:
            warning_signals.append("Incomplete start or end dates")
        else:
            if isinstance(start_date, str):
                try:
                    start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                except Exception:
                    start_date = None
            if isinstance(end_date, str):
                try:
                    end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                except Exception:
                    end_date = None

            if start_date and end_date:
                if end_date < start_date:
                    warning_signals.append("Event end date occurs before start date")
                else:
                    positive_signals.append("Chronologically valid start and end dates")

        # 3. Registration deadline check
        reg_deadline = event_data.get("registration_deadline")
        if reg_deadline:
            if isinstance(reg_deadline, str):
                try:
                    reg_deadline = datetime.fromisoformat(reg_deadline.replace("Z", "+00:00"))
                except Exception:
                    reg_deadline = None

            if reg_deadline and start_date and reg_deadline > start_date:
                warning_signals.append("Registration deadline is scheduled after event starts")
            elif reg_deadline:
                positive_signals.append("Explicit registration deadline identified")

        # 4. Geographic sanity rule (CRITICAL LOCATION RULE)
        # In-person events MUST have venue or city evidence
        fmt = event_data.get("format", "online").lower()
        if fmt in ("in_person", "hybrid"):
            venue = event_data.get("venue_name") or event_data.get("venue_address")
            city = event_data.get("city")
            region_id = event_data.get("region_id")
            if not venue and not city:
                warning_signals.append("Physical/Hybrid event lacks confirmed city or venue details")
            elif not region_id:
                warning_signals.append("Physical/Hybrid event location has not been mapped to a verified administrative region")
            else:
                positive_signals.append("Physical venue corroborated with administrative region code")
        elif fmt == "online":
            positive_signals.append("Online format confirmed; independent of physical venue constraints")

        # 5. Final decision threshold
        if warning_signals:
            if any("end date occurs before start date" in w or "Malformed" in w for w in warning_signals):
                decision = "needs_review"
            else:
                decision = "unverified"
        else:
            decision = "verified"

        return decision, positive_signals, warning_signals
