import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import case, func, or_, and_, desc, asc

# Stop words and filler expressions to clean from search queries
FILLER_EXPRESSIONS = [
    r"\bcollege students?\b",
    r"\buniversity students?\b",
    r"\bfor students?\b",
    r"\bfor developers?\b",
    r"\bnext month\b",
    r"\bthis week\b",
    r"\bthis month\b",
    r"\bupcoming\b",
    r"\ballow(?:s|ing)?\b",
    r"\baccept(?:s|ing)?\b",
    r"\bhappening\b",
    r"\btaking place\b",
    r"\bhosted (?:in|by|at)?\b",
    r"\bscheduled (?:in|for)?\b",
    r"\bwithin\b",
    r"\bevents?\b",
    r"\bopportunities?\b",
    r"\bprogram(?:s)?\b",
]

def parse_natural_language_search(query: str) -> Dict[str, Any]:
    """
    Parse natural-language search queries into validated structured filters and clean search terms.
    Handles phrases like:
    - 'AI hackathons in Telangana'
    - 'online cybersecurity competitions with registration still open'
    - 'free Python workshops for college students'
    - 'global developer conferences next month'
    - 'hackathons with deadlines within 7 days'
    - 'beginner-friendly machine-learning workshops'
    - 'events in Karnataka that allow individual participation'
    - 'open-source events that accept international participants'
    """
    if not query or not query.strip():
        return {
            "clean_query": "",
            "tokens": [],
            "extracted_filters": {},
            "has_structured_filters": False
        }

    raw = query.strip()
    q_lower = raw.lower()
    filters: Dict[str, Any] = {}
    tokens_to_remove = set()

    # 1. Category extraction
    if re.search(r"\bhackathons?\b", q_lower):
        filters["category"] = "hackathon"
        tokens_to_remove.update(["hackathon", "hackathons"])
    elif re.search(r"\bconferences?\b|\bsummits?\b", q_lower):
        filters["category"] = "conference"
        tokens_to_remove.update(["conference", "conferences", "summit", "summits"])
    elif re.search(r"\bworkshops?\b|\bbootcamps?\b", q_lower):
        filters["category"] = "workshop"
        tokens_to_remove.update(["workshop", "workshops", "bootcamp", "bootcamps"])
    elif re.search(r"\bcompetitions?\b|\bchallenges?\b|\bcontests?\b", q_lower):
        filters["category"] = "competition"
        tokens_to_remove.update(["competition", "competitions", "challenge", "challenges", "contest", "contests"])

    # 2. Format extraction
    if re.search(r"\bonline\b|\bremote\b|\bvirtual\b", q_lower):
        filters["format"] = "online"
        tokens_to_remove.update(["online", "remote", "virtual"])
    elif re.search(r"\bin[- ]person\b|\boffline\b|\bphysical\b", q_lower):
        filters["format"] = "in_person"
        tokens_to_remove.update(["in-person", "in person", "offline", "physical"])
    elif re.search(r"\bhybrid\b", q_lower):
        filters["format"] = "hybrid"
        tokens_to_remove.add("hybrid")

    # 3. Cost / Free
    if re.search(r"\bfree\b|\bno fee\b|\bzero cost\b|\bfree entry\b", q_lower):
        filters["is_free"] = True
        tokens_to_remove.update(["free", "no fee", "zero cost", "free entry"])

    # 4. Indian State / Hub extraction
    if re.search(r"\btelangana\b|\bhyderabad\b", q_lower):
        filters["state_slug"] = "telangana"
        tokens_to_remove.update(["telangana", "hyderabad", "in telangana", "in hyderabad"])
    elif re.search(r"\bkarnataka\b|\bbengaluru\b|\bbangalore\b", q_lower):
        filters["state_slug"] = "karnataka"
        tokens_to_remove.update(["karnataka", "bengaluru", "bangalore", "in karnataka", "in bengaluru", "in bangalore"])
    elif re.search(r"\bdelhi\b|\bncr\b|\bnew delhi\b", q_lower):
        filters["state_slug"] = "delhi"
        tokens_to_remove.update(["delhi", "ncr", "new delhi", "in delhi", "in ncr"])
    elif re.search(r"\bmaharashtra\b|\bmumbai\b|\bpune\b", q_lower):
        filters["state_slug"] = "maharashtra"
        tokens_to_remove.update(["maharashtra", "mumbai", "pune", "in maharashtra", "in mumbai", "in pune"])
    elif re.search(r"\btamil[- ]nadu\b|\bchennai\b", q_lower):
        filters["state_slug"] = "tamil-nadu"
        tokens_to_remove.update(["tamil nadu", "tamil-nadu", "chennai", "in chennai"])
    elif re.search(r"\bgujarat\b|\bgandhinagar\b|\bahmedabad\b", q_lower):
        filters["state_slug"] = "gujarat"
        tokens_to_remove.update(["gujarat", "gandhinagar", "ahmedabad"])
    elif re.search(r"\bgoa\b", q_lower):
        filters["state_slug"] = "goa"
        tokens_to_remove.update(["goa", "in goa"])
    elif re.search(r"\bkerala\b|\bkochi\b", q_lower):
        filters["state_slug"] = "kerala"
        tokens_to_remove.update(["kerala", "kochi", "in kerala"])

    # 5. Global scope
    if re.search(r"\bglobal\b|\bworldwide\b|\binternational\b", q_lower):
        if "state_slug" not in filters:
            filters["country_code"] = "GLOBAL"
        tokens_to_remove.update(["global", "worldwide", "international"])

    # 6. Status / Open registration
    if re.search(r"\bregistration (?:is )?still open\b|\bopen registration\b|\baccepting applications?\b", q_lower):
        filters["status"] = "upcoming"
        tokens_to_remove.update(["registration still open", "still open", "open registration", "registration is still open"])

    # 7. Deadlines within N days
    deadline_match = re.search(r"\bdeadlines? (?:is )?within (\d+|seven|three|five|ten|fourteen) days?\b", q_lower)
    if deadline_match:
        val_str = deadline_match.group(1)
        word_to_num = {"seven": 7, "three": 3, "five": 5, "ten": 10, "fourteen": 14}
        days = word_to_num.get(val_str, int(val_str) if val_str.isdigit() else 7)
        filters["deadline_within_days"] = days
        filters["sort_by"] = "deadline"
        tokens_to_remove.add(deadline_match.group(0))

    # 8. Individual participation
    if re.search(r"\bindividual(?: participation)?\b|\bsolo\b|\bsingle participant\b", q_lower):
        filters["team_size_min"] = 1
        tokens_to_remove.update(["individual participation", "individual", "solo", "single participant"])

    # 9. Clean remaining search terms
    clean_text = raw
    for tok in sorted(tokens_to_remove, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(tok)}\b", re.IGNORECASE)
        clean_text = pattern.sub("", clean_text)

    # Clean filler expressions
    for filler in FILLER_EXPRESSIONS:
        clean_text = re.sub(filler, "", clean_text, flags=re.IGNORECASE)

    # Clean residual connective words
    clean_text = re.sub(r"\b(in|for|with|that|and|of|to|a|an|the)\b", "", clean_text, flags=re.IGNORECASE)
    # Normalize hyphens inside words to spaces so 'beginner-friendly' matches 'beginner' and 'friendly'
    clean_text = clean_text.replace("-", " ")
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # Extract meaningful tokens (length >= 2, lowercased for uniform matching)
    tokens = [t.lower() for t in clean_text.split() if len(t) >= 2]

    return {
        "raw_query": raw,
        "clean_query": clean_text,
        "tokens": tokens,
        "extracted_filters": filters,
        "parsed": filters,
        "category": filters.get("category"),
        "format": filters.get("format"),
        "is_free": filters.get("is_free"),
        "state_slug": filters.get("state_slug"),
        "deadline_within_days": filters.get("deadline_within_days"),
        "team_size_min": filters.get("team_size_min"),
        "status": filters.get("status"),
        "has_structured_filters": len(filters) > 0
    }

def build_relevance_score(tokens: List[str], Event):
    """
    Constructs a weighted relevance score case expression for ranking search results.
    Sums points for each matching token:
    - Title match: +10 points
    - Tags match: +8 points
    - City / State match: +6 points
    - Eligibility match: +4 points
    - Description match: +3 points
    - Active status: +5 points
    - Verified listing: +3 points
    """
    score = case((Event.status == "upcoming", 5), else_=0) + case((Event.verification_status == "verified", 3), else_=0)
    if not tokens:
        return score

    for token in tokens[:5]:
        term = f"%{token}%"
        score = score + (
            case((Event.title.ilike(term), 10), else_=0) +
            case((Event.tags.ilike(term), 8), else_=0) +
            case((Event.city.ilike(term), 6), else_=0) +
            case((Event.eligibility.ilike(term), 4), else_=0) +
            case((Event.description.ilike(term), 3), else_=0)
        )
    return score
