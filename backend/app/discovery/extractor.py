import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup

def parse_iso_or_fuzzy_date(date_str: str) -> Optional[datetime]:
    """Parse ISO8601 or common date formats safely."""
    if not date_str:
        return None
    # Try ISO
    try:
        clean = date_str.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        pass

    # Try standard YYYY-MM-DD
    match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=timezone.utc)
        except Exception:
            pass

    return None

class StructuredMetadataExtractor:
    """
    Extracts high-fidelity event metadata from HTML pages using deterministic parsing:
    1. Schema.org JSON-LD Event metadata
    2. OpenGraph / Twitter metadata
    3. Semantic HTML tags
    """

    @classmethod
    def extract_from_html(cls, html_content: str, source_url: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "title": None,
            "description": None,
            "start_date": None,
            "end_date": None,
            "registration_deadline": None,
            "format": "online",
            "registration_url": source_url,
            "organizer_name": None,
            "venue_name": None,
            "city": None,
            "is_free": True,
            "raw_json_ld": None,
            "extraction_method": "deterministic_html"
        }

        if not html_content:
            return result

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Search for Schema.org JSON-LD
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("@graph", [data])
                else:
                    items = []

                for item in items:
                    if isinstance(item, dict) and item.get("@type") in ("Event", "Hackathon", "EducationEvent", "BusinessEvent"):
                        result["raw_json_ld"] = item
                        result["title"] = item.get("name")
                        result["description"] = item.get("description")
                        
                        start = parse_iso_or_fuzzy_date(item.get("startDate"))
                        if start:
                            result["start_date"] = start
                        
                        end = parse_iso_or_fuzzy_date(item.get("endDate"))
                        if end:
                            result["end_date"] = end

                        # Location & Format
                        loc = item.get("location")
                        if isinstance(loc, dict):
                            if loc.get("@type") == "VirtualLocation":
                                result["format"] = "online"
                            elif loc.get("@type") == "Place":
                                result["format"] = "in_person"
                                result["venue_name"] = loc.get("name")
                                addr = loc.get("address")
                                if isinstance(addr, dict):
                                    result["city"] = addr.get("addressLocality")
                        
                        # Organizer
                        org = item.get("organizer")
                        if isinstance(org, dict):
                            result["organizer_name"] = org.get("name")
                        elif isinstance(org, str):
                            result["organizer_name"] = org

                        # Offers / Fee
                        offers = item.get("offers")
                        if isinstance(offers, dict):
                            price = offers.get("price")
                            if price and str(price) not in ("0", "0.0", "free"):
                                result["is_free"] = False

                        result["extraction_method"] = "json_ld_schema"
                        break
            except Exception:
                continue

        # 2. OpenGraph Fallbacks if fields missing
        if not result["title"]:
            og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
            if og_title and og_title.get("content"):
                result["title"] = og_title["content"].strip()
            elif soup.title and soup.title.string:
                result["title"] = soup.title.string.strip()

        if not result["description"]:
            og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
            if og_desc and og_desc.get("content"):
                result["description"] = og_desc["content"].strip()

        og_url = soup.find("meta", property="og:url")
        if og_url and og_url.get("content"):
            result["registration_url"] = og_url["content"].strip()

        return result
