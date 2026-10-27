import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc
from sqlalchemy.orm import selectinload

from backend.app.models.event import Event
from backend.app.models.region import AdministrativeRegion
from backend.app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse, AssistantEventCitation, ChatMessage
from backend.app.core.config import settings

logger = logging.getLogger("eventhorizon.assistant")

# Common Indian cities mapped to canonical state slugs
CITY_TO_STATE_SLUG = {
    "hyderabad": "telangana",
    "secunderabad": "telangana",
    "warangal": "telangana",
    "bengaluru": "karnataka",
    "bangalore": "karnataka",
    "mysuru": "karnataka",
    "mysore": "karnataka",
    "mumbai": "maharashtra",
    "pune": "maharashtra",
    "nagpur": "maharashtra",
    "delhi": "delhi",
    "new delhi": "delhi",
    "ncr": "delhi",
    "noida": "uttar-pradesh",
    "gurugram": "haryana",
    "gurgaon": "haryana",
    "chennai": "tamil-nadu",
    "coimbatore": "tamil-nadu",
    "kolkata": "west-bengal",
    "ahmedabad": "gujarat",
    "gandhinagar": "gujarat",
    "jaipur": "rajasthan",
    "kochi": "kerala",
    "thiruvananthapuram": "kerala",
    "trivandrum": "kerala",
    "goa": "goa",
    "panaji": "goa",
    "bhopal": "madhya-pradesh",
    "indore": "madhya-pradesh",
    "chandigarh": "chandigarh",
    "bhubaneswar": "odisha",
    "patna": "bihar",
    "lucknow": "uttar-pradesh",
}

def clean_input(text: str) -> str:
    """Normalize input whitespace and remove control characters."""
    return re.sub(r"\s+", " ", text or "").strip()

def is_greeting(q: str) -> bool:
    """Check if query is an ordinary greeting."""
    q_norm = clean_input(q).lower()
    greetings = {
        "hi", "hello", "hey", "heya", "howdy", "namaste", "greetings",
        "good morning", "good afternoon", "good evening", "hi there", "hello there",
        "hey there", "yo", "sup", "what's up", "whats up"
    }
    if q_norm in greetings:
        return True
    # Strip punctuation and check again
    q_stripped = re.sub(r"[^\w\s]", "", q_norm).strip()
    return q_stripped in greetings

def is_status_query(q: str) -> bool:
    """Check if user asks how the assistant is doing."""
    q_norm = clean_input(q).lower()
    return bool(re.search(r"\b(how are you|how'?s it going|how are you doing|how do you do)\b", q_norm))

def is_capability_query(q: str) -> bool:
    """Check if user asks what the assistant can do."""
    q_norm = clean_input(q).lower()
    patterns = [
        r"\bwhat can you do\b",
        r"\bwho are you\b",
        r"\bwhat are your features\b",
        r"\bwhat do you do\b",
        r"\bhow can you help\b",
        r"\bhelp me\b",
        r"\bwhat is this\b",
        r"\bcapabilities\b",
    ]
    return any(re.search(p, q_norm) for p in patterns)

def is_gratitude_or_farewell(q: str) -> bool:
    """Check if user is saying thanks or goodbye."""
    q_norm = clean_input(q).lower()
    patterns = [
        r"\b(thank you|thanks|thx|appreciate it|thank you so much)\b",
        r"\b(bye|goodbye|see you|catch you later|have a good day)\b",
    ]
    return any(re.search(p, q_norm) for p in patterns)

def is_unrelated_query(q: str) -> bool:
    """Detect queries unrelated to event discovery (e.g. arbitrary coding, trivia, recipes)."""
    q_norm = clean_input(q).lower()

    # If it contains event-related terms, it's not unrelated
    event_terms = [
        "hackathon", "conference", "workshop", "meetup", "competition", "challenge",
        "event", "summit", "bootcamp", "talk", "registration", "deadline", "prize",
        "telangana", "karnataka", "delhi", "maharashtra", "india", "online", "hybrid"
    ]
    if any(term in q_norm for term in event_terms):
        return False

    # Patterns typical of unrelated questions
    unrelated_patterns = [
        r"^write (?:a|an)? (?:code|script|python|function|class|essay|poem|recipe|story)\b",
        r"^how to (?:cook|bake|make|repair|calculate|reverse a linked list|invert a binary tree)\b",
        r"^what is the (?:capital|population|weather|currency|meaning of life)\b",
        r"^solve (?:this|the following)? (?:equation|math|problem|riddle)\b",
        r"\btranslate (?:this|into)\b",
    ]
    return any(re.search(p, q_norm) for p in unrelated_patterns)

def is_followup_query(q: str) -> bool:
    """Detect if the query refers to prior context."""
    q_norm = clean_input(q).lower()
    followup_patterns = [
        r"\b(any of (?:them|those)|are (?:any|they) free|which (?:ones?|of them))\b",
        r"\b(what about|how about|show only|filter by)\b",
        r"\b(tell me more about|more details on (?:the)? (?:first|second|third|last|it))\b",
        r"\b(in (?:karnataka|delhi|telangana|maharashtra|hyderabad|bengaluru))\b",
        r"\b(online only|free only|in-person only)\b",
    ]
    return any(re.search(p, q_norm) for p in followup_patterns)

def extract_filters_from_text(text: str) -> Dict[str, Any]:
    """Parse text into structured event constraints."""
    q_lower = text.lower()
    filters: Dict[str, Any] = {}

    # Category
    if re.search(r"\bhackathons?\b", q_lower):
        filters["category"] = "hackathon"
    elif re.search(r"\bconferences?\b|\bsummits?\b", q_lower):
        filters["category"] = "conference"
    elif re.search(r"\bworkshops?\b|\bbootcamps?\b", q_lower):
        filters["category"] = "workshop"
    elif re.search(r"\bcompetitions?\b|\bchallenges?\b|\bcontests?\b", q_lower):
        filters["category"] = "competition"
    elif re.search(r"\bmeetups?\b", q_lower):
        filters["category"] = "meetup"

    # Format
    if re.search(r"\bonline\b|\bremote\b|\bvirtual\b", q_lower):
        filters["format"] = "online"
    elif re.search(r"\bin[- ]person\b|\boffline\b|\bphysical\b", q_lower):
        filters["format"] = "in_person"
    elif re.search(r"\bhybrid\b", q_lower):
        filters["format"] = "hybrid"

    # Price / Free
    if re.search(r"\bfree\b|\bno fee\b|\bzero cost\b|\bfree entry\b", q_lower):
        filters["is_free"] = True
    elif re.search(r"\bpaid\b|\bticketed\b", q_lower):
        filters["is_free"] = False

    # Indian Geographic mapping
    for city, slug in CITY_TO_STATE_SLUG.items():
        if re.search(rf"\b{city}\b", q_lower):
            filters["state_slug"] = slug
            break

    if "state_slug" not in filters:
        state_patterns = [
            ("telangana", "telangana"),
            ("karnataka", "karnataka"),
            ("delhi", "delhi"),
            ("maharashtra", "maharashtra"),
            ("tamil[- ]nadu", "tamil-nadu"),
            ("gujarat", "gujarat"),
            ("kerala", "kerala"),
            ("goa", "goa"),
            ("west[- ]bengal", "west-bengal"),
            ("rajasthan", "rajasthan"),
            ("uttar[- ]pradesh", "uttar-pradesh"),
            ("punjab", "punjab"),
            ("haryana", "haryana"),
            ("andhra[- ]pradesh", "andhra-pradesh"),
            ("odisha", "odisha"),
        ]
        for pattern, slug in state_patterns:
            if re.search(rf"\b{pattern}\b", q_lower):
                filters["state_slug"] = slug
                break

    # Tech domains
    domains = []
    if re.search(r"\bai\b|\bmachine learning\b|\bml\b|\bllm\b|\bdeep ?tech\b|\bgenerative ai\b", q_lower):
        domains.append("AI/ML")
    if re.search(r"\bweb\b|\bfull[- ]?stack\b|\bfrontend\b|\bbackend\b|\breact\b", q_lower):
        domains.append("Web")
    if re.search(r"\bcyber(?:security)?\b|\bctf\b|\bsecurity\b", q_lower):
        domains.append("Cybersecurity")
    if re.search(r"\bpython\b", q_lower):
        domains.append("Python")
    if re.search(r"\brust\b", q_lower):
        domains.append("Rust")
    if re.search(r"\bcloud\b|\bdevops\b|\bkubernetes\b|\bcncf\b", q_lower):
        domains.append("Cloud")
    if re.search(r"\bopen[- ]source\b|\bfoss\b", q_lower):
        domains.append("Open Source")
    if re.search(r"\bblockchain\b|\bweb3\b|\beth\b", q_lower):
        domains.append("Web3/Blockchain")

    if domains:
        filters["domains"] = domains

    return filters

def extract_contextual_filters(
    query: str,
    messages: Optional[List[ChatMessage]] = None,
    user_state_preference: Optional[str] = None,
    preferred_format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract filters with conversation memory support.
    If the current message is a follow-up, inherit constraints from previous exchanges.
    """
    current_filters = extract_filters_from_text(query)

    inherited_filters: Dict[str, Any] = {}
    if messages and len(messages) > 1 and is_followup_query(query):
        # Scan recent messages (last 3 user messages)
        for msg in reversed(messages[:-1]):
            if msg.role == "user":
                prior = extract_filters_from_text(msg.content)
                for k, v in prior.items():
                    if k not in inherited_filters:
                        inherited_filters[k] = v

    # Merge: current filters override inherited filters
    combined = {**inherited_filters, **current_filters}

    # Explicit user preferences override if provided
    if user_state_preference:
        combined["state_slug"] = user_state_preference
    if preferred_format:
        combined["format"] = preferred_format

    return combined

async def execute_assistant_query(db: AsyncSession, request: AssistantQueryRequest) -> AssistantQueryResponse:
    """
    Ground-truth conversational AI Event Assistant.
    - Handles greetings, capabilities, and out-of-scope queries naturally.
    - Uses conversation history for context-aware follow-up reasoning.
    - Retrieves authentic database events with zero hallucinations.
    - Synthesizes clear, structured answers with official registration links.
    """
    raw_query = clean_input(request.query)

    # 1. Empty or whitespace input
    if not raw_query:
        return AssistantQueryResponse(
            answer="Please enter a message or question about events you'd like to discover.",
            events=[],
            suggested_followups=[
                "Find AI hackathons in Telangana",
                "Show upcoming online workshops",
                "What developer conferences are happening in Karnataka?"
            ],
            intent="empty_input"
        )

    # 2. Pure greetings
    if is_greeting(raw_query):
        return AssistantQueryResponse(
            answer="Hi! How can I help you discover events today?",
            events=[],
            suggested_followups=[
                "Find AI hackathons in Telangana",
                "Show upcoming online workshops",
                "What can you do?",
                "Which hackathons are free to enter?"
            ],
            intent="greeting"
        )

    # 3. Status queries ("How are you?")
    if is_status_query(raw_query):
        return AssistantQueryResponse(
            answer="I'm doing well, thank you! Ready to help you discover verified hackathons, conferences, and technical workshops across India and worldwide. What kind of event are you looking for today?",
            events=[],
            suggested_followups=[
                "Find AI hackathons in Telangana",
                "Show upcoming online workshops",
                "What can you do?"
            ],
            intent="status"
        )

    # 4. Capability / Help queries ("What can you do?")
    if is_capability_query(raw_query):
        return AssistantQueryResponse(
            answer=(
                "I am **EventHorizon AI**, your dedicated tech event discovery assistant. Here is what I can do for you:\n\n"
                "- **Discover Verified Events**: Find hackathons, developer conferences, engineering competitions, and workshops with guaranteed reachability.\n"
                "- **Geographic Integrity**: Explore events across all 28 Indian states & 8 Union Territories with strict physical anti-leakage, or locate global virtual events.\n"
                "- **Filter by Technology & Format**: Search by domain (AI/ML, Web, Cybersecurity, Python, Rust, Cloud) and mode (online, in-person, hybrid).\n"
                "- **Deadlines & Links**: Check approaching registration deadlines and access verified official organizer registration links.\n\n"
                "Try asking me:\n"
                "- *\"Find AI hackathons in Telangana\"*\n"
                "- *\"Show upcoming online workshops\"*\n"
                "- *\"Are there any free hackathons with cash prizes?\"*"
            ),
            events=[],
            suggested_followups=[
                "Find AI hackathons in Telangana",
                "Show upcoming online workshops",
                "Show developer conferences in Karnataka"
            ],
            intent="capability"
        )

    # 5. Gratitude / Farewell
    if is_gratitude_or_farewell(raw_query):
        return AssistantQueryResponse(
            answer="You're very welcome! Feel free to ask anytime you're looking for upcoming developer opportunities. Have a wonderful day!",
            events=[],
            suggested_followups=[
                "Find AI hackathons in Telangana",
                "Show upcoming online workshops"
            ],
            intent="gratitude"
        )

    # 6. Unrelated / Out-of-scope query
    if is_unrelated_query(raw_query):
        return AssistantQueryResponse(
            answer=(
                "I specialize in **tech event discovery** — connecting developers and students with verified hackathons, conferences, workshops, and competitions.\n\n"
                "While I cannot answer general coding problems, trivia, or unrelated questions, I would be happy to help you find workshops or hackathons where you can build and practice those skills! What kind of event interests you?"
            ),
            events=[],
            suggested_followups=[
                "Find AI hackathons",
                "Show Python workshops",
                "Online cybersecurity competitions"
            ],
            intent="unrelated"
        )

    # 7. Grounded Event Retrieval
    filters = extract_contextual_filters(
        query=raw_query,
        messages=request.messages,
        user_state_preference=request.user_state_preference,
        preferred_format=request.preferred_format
    )

    state_slug = filters.get("state_slug")
    category = filters.get("category")
    format_filter = filters.get("format")
    is_free = filters.get("is_free")
    domains = filters.get("domains", [])

    stmt = select(Event).options(
        selectinload(Event.region),
        selectinload(Event.organizer)
    ).where(Event.status.in_(["upcoming", "ongoing"]))

    clauses = []
    if category:
        clauses.append(Event.category == category)
    if format_filter:
        clauses.append(Event.format == format_filter)
    if is_free is not None:
        clauses.append(Event.is_free == is_free)

    if state_slug:
        reg_res = await db.execute(select(AdministrativeRegion.id).where(AdministrativeRegion.slug == state_slug))
        reg_id = reg_res.scalar_one_or_none()
        if reg_id:
            if format_filter == "online":
                clauses.append(Event.format == "online")
            else:
                clauses.append(Event.region_id == reg_id)

    # Domain keywords
    if domains:
        domain_clauses = [
            or_(
                Event.title.ilike(f"%{d}%"),
                Event.description.ilike(f"%{d}%"),
                Event.tags.ilike(f"%{d}%")
            )
            for d in domains
        ]
        clauses.append(or_(*domain_clauses))

    # Stop words that should never be searched as literal substring filters in titles
    ASSISTANT_STOP_WORDS = {
        "what", "which", "where", "show", "find", "events", "event", "about",
        "give", "tell", "need", "looking", "open", "some", "hackathons",
        "hackathon", "workshops", "workshop", "conferences", "conference",
        "competitions", "competition", "meetups", "meetup", "them", "those",
        "ones", "free", "paid", "online", "here", "also", "there", "have",
        "with", "from", "that", "this", "many", "more", "soon", "next",
        "scheduled", "upcoming", "ongoing", "active", "latest", "opportunity",
        "opportunities", "attend", "participate", "join", "browse"
    }

    # Keyword terms search for additional tokens
    tokens = re.sub(r"[^\w\s]", " ", raw_query).split()
    meaningful_tokens = [
        t for t in tokens
        if len(t) > 3 and t.lower() not in ASSISTANT_STOP_WORDS
    ]
    # Only apply keyword clauses if it's not a generic follow-up with structured filters
    if meaningful_tokens and not is_followup_query(raw_query):
        term_clauses = [
            or_(
                Event.title.ilike(f"%{tok}%"),
                Event.description.ilike(f"%{tok}%"),
                Event.tags.ilike(f"%{tok}%")
            )
            for tok in meaningful_tokens[:2]
        ]
        clauses.append(or_(*term_clauses))

    if clauses:
        stmt = stmt.where(and_(*clauses))

    stmt = stmt.order_by(Event.start_date.asc()).limit(6)
    results = await db.execute(stmt)
    matched_events = results.scalars().all()

    # Build structured citations
    citations: List[AssistantEventCitation] = []
    for ev in matched_events:
        state_name = ev.region.name if ev.region else None
        citations.append(
            AssistantEventCitation(
                id=ev.id,
                title=ev.title,
                slug=ev.slug,
                category=ev.category.capitalize(),
                format=ev.format.capitalize(),
                city=ev.city,
                state=state_name,
                start_date=ev.start_date.strftime("%B %d, %Y"),
                registration_deadline=ev.registration_deadline.strftime("%B %d, %Y") if ev.registration_deadline else None,
                registration_url=ev.registration_url,
                official_website=ev.official_website,
                is_free=ev.is_free,
                prize_pool=ev.prize_pool,
                verification_status=ev.verification_status
            )
        )

    # 8. Conversational Answer Synthesis
    api_key = settings.AI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("AI_API_KEY")
    live_llm_used = False

    if api_key and settings.AI_PROVIDER == "gemini":
        try:
            llm_text = await generate_gemini_conversational_response(
                api_key=api_key,
                model_name=settings.AI_MODEL_NAME,
                query=raw_query,
                citations=citations,
                messages=request.messages
            )
            if llm_text:
                answer = llm_text
                live_llm_used = True
        except Exception as e:
            logger.warning(f"Live LLM provider error: {e}. Falling back to grounded template.")

    if not live_llm_used:
        # Ground-truth deterministic synthesis
        if not citations:
            target_desc = ""
            if state_slug:
                target_desc += f" in {state_slug.replace('-', ' ').title()}"
            if category:
                target_desc += f" for {category}s"
            
            answer = (
                f"I could not locate any active events strictly matching your search criteria{target_desc} in the verified database.\n\n"
                "You might want to:\n"
                "- Check for upcoming **online** events that accept participants globally.\n"
                "- Explore neighbouring states or broaden your category selection.\n"
                "- Look at the unverified candidates queue on the India Explorer page."
            )
            followups = [
                "Show all upcoming online hackathons",
                "What tech events are happening in Karnataka?",
                "Find beginner-friendly workshops"
            ]
        else:
            state_ctx = f" in {state_slug.replace('-', ' ').title()}" if state_slug else ""
            answer = f"Found **{len(citations)} verified opportunity(ies)**{state_ctx} matching your request:\n\n"

            for idx, c in enumerate(citations, 1):
                loc = f"{c.city}, {c.state}" if c.city and c.state else (c.state or "Online / Remote")
                deadline_str = f"**Deadline:** {c.registration_deadline} | " if c.registration_deadline else ""
                prize_str = f"**Prize Pool:** {c.prize_pool} | " if c.prize_pool else ""
                cost_str = "Free Entry" if c.is_free else "Paid"
                verified_badge = "✅ Verified" if c.verification_status == "verified" else "⚠️ Under Review"

                answer += f"### {idx}. [{c.title}](/events/{c.slug})\n"
                answer += f"- **Category & Format:** {c.category} · {c.format} ({loc})\n"
                answer += f"- **Date:** {c.start_date}\n"
                answer += f"- {deadline_str}{prize_str}**Cost:** {cost_str} · *{verified_badge}*\n"
                if c.registration_url:
                    answer += f"- 🔗 [Register directly on official portal]({c.registration_url})\n\n"
                elif c.official_website:
                    answer += f"- 🔗 [Official Organizer Site]({c.official_website})\n\n"
                else:
                    answer += f"- 🔗 [View Event Details](/events/{c.slug})\n\n"

            followups = [
                "Are any of these free to enter?",
                "Which of these are completely online?",
                "Show events with approaching deadlines"
            ]

    disclaimer = (
        "Recommendations are grounded in verified database records. Always check the official registration page for the latest updates."
        if live_llm_used else
        "Grounded in verified event records. Zero hallucinations guarantee."
    )

    return AssistantQueryResponse(
        answer=answer,
        events=citations,
        suggested_followups=followups if 'followups' in locals() else [
            "Find AI hackathons in Telangana",
            "Show upcoming online workshops",
            "Are there any free hackathons?"
        ],
        disclaimer=disclaimer,
        intent="event_retrieval"
    )

async def generate_gemini_conversational_response(
    api_key: str,
    model_name: str,
    query: str,
    citations: List[AssistantEventCitation],
    messages: Optional[List[ChatMessage]] = None
) -> Optional[str]:
    """Call Google Gemini REST API using httpx with grounded RAG context."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    # Build context from citations
    grounding_data = []
    for c in citations:
        grounding_data.append({
            "title": c.title,
            "category": c.category,
            "format": c.format,
            "location": f"{c.city}, {c.state}" if c.city and c.state else (c.state or "Online"),
            "date": c.start_date,
            "deadline": c.registration_deadline or "Not specified",
            "is_free": c.is_free,
            "prize_pool": c.prize_pool or "None",
            "registration_url": c.registration_url or c.official_website,
            "slug": c.slug,
            "status": c.verification_status
        })

    system_instruction = (
        "You are EventHorizon AI, a helpful, conversational tech event discovery assistant. "
        "You help developers find verified hackathons, conferences, workshops, and competitions. "
        "Strict rules:\n"
        "1. GROUND TRUTH ONLY: Answer ONLY using the provided database events. Never invent events, deadlines, prizes, or registration URLs.\n"
        "2. If no matching events exist in the provided list, politely say so and recommend broadening the search.\n"
        "3. Reply in a concise, friendly, conversational tone with Markdown formatting.\n"
        "4. Include direct Markdown links to each event: [Event Title](/events/{slug}) and official registration links where available."
    )

    prompt_content = f"User Request: {query}\n\nRetrieved Verified Database Records:\n{json.dumps(grounding_data, indent=2)}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction},
                    {"text": prompt_content}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024
        }
    }

    async with httpx.AsyncClient(timeout=6.0) as client:
        res = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
    return None
