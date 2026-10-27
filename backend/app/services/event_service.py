import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload

from backend.app.models.event import Event
from backend.app.models.region import AdministrativeRegion
from backend.app.models.organizer import Organizer
from backend.app.models.observation import EventSourceObservation
from backend.app.models.saved_event import EventReport, SavedEvent
from backend.app.schemas.event import EventCreate, EventUpdate, EventReportCreate
from backend.app.services.url_service import normalize_event_url, validate_url_syntax, verify_url_destination
from backend.app.services.search_service import parse_natural_language_search, build_relevance_score

def generate_slug(title: str, existing_id: Optional[int] = None) -> str:
    """Generate a clean, collision-resistant slug."""
    slug = re.sub(r"[^\w\s-]", "", title.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", slug)
    if not slug:
        slug = "event"
    if existing_id:
        slug = f"{slug[:280]}-{existing_id}"
    return slug[:300]

async def get_events(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    category: Optional[str] = None,
    format: Optional[str] = None, # online, in_person, hybrid
    status: Optional[str] = None, # upcoming, ongoing, completed, etc.
    verification_status: Optional[str] = None, # verified, unverified, needs_review
    country_code: Optional[str] = None,
    state_slug: Optional[str] = None,
    region_id: Optional[int] = None,
    is_free: Optional[bool] = None,
    include_online_in_state: bool = False,
    sort_by: str = "start_date", # start_date, deadline, created_at
    date_preset: Optional[str] = None, # today, this_week, this_month, next_30_days, next_90_days
    start_date_gte: Optional[datetime] = None,
    start_date_lte: Optional[datetime] = None,
) -> Tuple[List[Event], int]:
    """
    Search and filter events with strict geographic anti-leakage rules and intelligent natural-language understanding.
    """
    stmt = select(Event).options(
        selectinload(Event.region),
        selectinload(Event.organizer),
        selectinload(Event.observations)
    )
    count_stmt = select(func.count(Event.id))

    filters = []
    relevance_expr = None

    # Intelligent Natural Language Search Parser
    search_tokens = []
    if query and query.strip():
        parsed = parse_natural_language_search(query)
        extracted = parsed["extracted_filters"]
        search_tokens = parsed["tokens"]
        
        # Merge inferred filters if not explicitly overridden by user
        if not category or category.lower() == "all":
            category = extracted.get("category")
        if not format or format.lower() == "all":
            format = extracted.get("format")
        if is_free is None:
            is_free = extracted.get("is_free")
        if not state_slug and not region_id:
            state_slug = extracted.get("state_slug")
        if not country_code or country_code.upper() == "ALL":
            country_code = extracted.get("country_code")
        if not status or status.lower() == "all":
            status = extracted.get("status")
        if "deadline_within_days" in extracted:
            now_utc = datetime.now(timezone.utc)
            max_deadline = now_utc + timedelta(days=extracted["deadline_within_days"])
            filters.append(
                and_(
                    Event.registration_deadline >= now_utc,
                    Event.registration_deadline <= max_deadline
                )
            )
        if "team_size_min" in extracted:
            filters.append(Event.team_size_min <= extracted["team_size_min"])
        if "sort_by" in extracted and sort_by == "start_date":
            sort_by = extracted["sort_by"]

        # If there are residual keyword search tokens, filter by them
        if search_tokens:
            for tok in search_tokens[:3]:
                tok_term = f"%{tok}%"
                filters.append(
                    or_(
                        Event.title.ilike(tok_term),
                        Event.description.ilike(tok_term),
                        Event.city.ilike(tok_term),
                        Event.tags.ilike(tok_term),
                        Event.eligibility.ilike(tok_term)
                    )
                )
            relevance_expr = build_relevance_score(search_tokens, Event)
        elif not parsed["has_structured_filters"]:
            # Fallback if no filters extracted and no tokens left
            q_term = f"%{query.strip()}%"
            filters.append(
                or_(
                    Event.title.ilike(q_term),
                    Event.description.ilike(q_term),
                    Event.city.ilike(q_term),
                    Event.tags.ilike(q_term),
                    Event.eligibility.ilike(q_term)
                )
            )
            relevance_expr = build_relevance_score([query.strip()], Event)
        else:
            relevance_expr = build_relevance_score([], Event)

    # Category filter
    if category and category.lower() != "all":
        filters.append(Event.category == category.lower())

    # Format filter (online, in_person, hybrid)
    if format and format.lower() != "all":
        filters.append(Event.format == format.lower())

    # Status filter
    if status and status.lower() != "all":
        filters.append(Event.status == status.lower())

    # Verification status filter
    if verification_status and verification_status.lower() != "all":
        filters.append(Event.verification_status == verification_status.lower())

    # Country filter
    if country_code and country_code.upper() != "ALL":
        filters.append(Event.country_code == country_code.upper())

    # Price / Free filter
    if is_free is not None:
        filters.append(Event.is_free == is_free)

    # Date range & preset filtering
    now_utc = datetime.now(timezone.utc)
    if date_preset:
        dp = date_preset.lower()
        if dp == "today":
            today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            filters.append(and_(Event.start_date >= today_start, Event.start_date < today_end))
        elif dp == "this_week":
            filters.append(and_(Event.start_date >= now_utc, Event.start_date <= now_utc + timedelta(days=7)))
        elif dp in ("this_month", "next_30_days"):
            filters.append(and_(Event.start_date >= now_utc, Event.start_date <= now_utc + timedelta(days=30)))
        elif dp == "next_90_days":
            filters.append(and_(Event.start_date >= now_utc, Event.start_date <= now_utc + timedelta(days=90)))

    if start_date_gte:
        filters.append(Event.start_date >= start_date_gte)
    if start_date_lte:
        filters.append(Event.start_date <= start_date_lte)

    # STRICT GEOGRAPHIC RESOLUTION:
    # If state_slug is supplied, resolve its ID
    resolved_region_id = region_id
    if state_slug and not resolved_region_id:
        reg_stmt = select(AdministrativeRegion.id).where(AdministrativeRegion.slug == state_slug)
        reg_res = await db.execute(reg_stmt)
        resolved_region_id = reg_res.scalar_one_or_none()

    if resolved_region_id is not None:
        # Cross-state leakage prevention:
        # In physical mode: ONLY events with matching region_id
        if include_online_in_state:
            filters.append(
                or_(
                    Event.region_id == resolved_region_id,
                    Event.format == "online"
                )
            )
        else:
            filters.append(Event.region_id == resolved_region_id)

    if filters:
        stmt = stmt.where(and_(*filters))
        count_stmt = count_stmt.where(and_(*filters))

    # Sorting & Relevance Ranking
    if sort_by == "relevance" and relevance_expr is not None:
        stmt = stmt.order_by(desc(relevance_expr), asc(Event.start_date))
    elif sort_by == "deadline":
        stmt = stmt.order_by(Event.registration_deadline.asc().nulls_last(), Event.start_date.asc())
    elif sort_by == "created_at":
        stmt = stmt.order_by(desc(Event.created_at))
    else: # default: relevance if query provided, start_date otherwise
        if relevance_expr is not None:
            stmt = stmt.order_by(desc(relevance_expr), asc(Event.start_date))
        else:
            stmt = stmt.order_by(asc(Event.start_date))

    # Total count
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    events_res = await db.execute(stmt)
    events = events_res.scalars().all()

    return events, total

async def get_event_by_id_or_slug(db: AsyncSession, identifier: str) -> Optional[Event]:
    """Retrieve an event by numeric ID or unique slug, with full relationships."""
    stmt = select(Event).options(
        selectinload(Event.region),
        selectinload(Event.organizer),
        selectinload(Event.observations).selectinload(EventSourceObservation.source)
    )
    if identifier.isdigit():
        stmt = stmt.where(Event.id == int(identifier))
    else:
        stmt = stmt.where(Event.slug == identifier)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_event(db: AsyncSession, payload: EventCreate) -> Event:
    """Create a new event record with auto-slugification and organizer binding."""
    # Find or create organizer if name supplied
    organizer_id = payload.organizer_id
    if not organizer_id and payload.organizer_name:
        org_slug = generate_slug(payload.organizer_name)
        org_stmt = select(Organizer).where(Organizer.slug == org_slug)
        org_res = await db.execute(org_stmt)
        org_obj = org_res.scalar_one_or_none()
        if not org_obj:
            org_obj = Organizer(name=payload.organizer_name, slug=org_slug)
            db.add(org_obj)
            await db.flush()
        organizer_id = org_obj.id

    base_slug = generate_slug(payload.title)
    # Check for existing slug collision
    slug_check = await db.execute(select(Event.id).where(Event.slug == base_slug))
    if slug_check.scalar_one_or_none():
        base_slug = f"{base_slug}-{int(datetime.now(timezone.utc).timestamp())}"

    event_dict = payload.model_dump(exclude={"organizer_name", "organizer_id"})
    
    # Safely normalize URLs without destroying query params
    if event_dict.get("registration_url"):
        event_dict["registration_url"] = normalize_event_url(event_dict["registration_url"])
    if event_dict.get("official_website"):
        event_dict["official_website"] = normalize_event_url(event_dict["official_website"])
    if event_dict.get("source_url"):
        event_dict["source_url"] = normalize_event_url(event_dict["source_url"])

    event = Event(
        **event_dict,
        slug=base_slug,
        organizer_id=organizer_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def update_event(db: AsyncSession, event_id: int, payload: EventUpdate) -> Optional[Event]:
    """Update event fields with timestamp bump."""
    event = await get_event_by_id_or_slug(db, str(event_id))
    if not event:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if "title" in update_data and update_data["title"] and update_data["title"] != event.title:
        event.slug = generate_slug(update_data["title"], event.id)

    # Safely normalize URLs
    if "registration_url" in update_data and update_data["registration_url"]:
        update_data["registration_url"] = normalize_event_url(update_data["registration_url"])
    if "official_website" in update_data and update_data["official_website"]:
        update_data["official_website"] = normalize_event_url(update_data["official_website"])
    if "source_url" in update_data and update_data["source_url"]:
        update_data["source_url"] = normalize_event_url(update_data["source_url"])

    for field, value in update_data.items():
        setattr(event, field, value)

    event.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(event)
    return event

async def delete_event(db: AsyncSession, event_id: int) -> bool:
    """Delete an event and cascade-remove related observations and bookmarks."""
    event = await get_event_by_id_or_slug(db, str(event_id))
    if not event:
        return False
    await db.delete(event)
    await db.commit()
    return True

async def report_event(db: AsyncSession, event_id: int, payload: EventReportCreate) -> EventReport:
    """Submit a factual inaccuracy or link issue report for an event."""
    report = EventReport(
        event_id=event_id,
        reporter_email=payload.reporter_email,
        issue_type=payload.issue_type,
        description=payload.description,
        created_at=datetime.now(timezone.utc)
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

async def check_and_update_event_link(db: AsyncSession, event_id: int) -> Dict[str, Any]:
    """Verify live destination of an event's registration URL and record audit outcome."""
    event = await get_event_by_id_or_slug(db, str(event_id))
    if not event:
        return {"error": "Event not found"}

    url_to_check = event.registration_url or event.official_website
    if not url_to_check:
        event.link_status = "unverified"
        event.link_last_checked_at = datetime.now(timezone.utc)
        await db.commit()
        return {"status": "unverified", "message": "No URL configured"}

    result = await verify_url_destination(url_to_check)
    event.link_status = result["status"]
    event.link_http_status = result["http_status"]
    event.link_last_checked_at = datetime.now(timezone.utc)
    event.link_error = result["error"]
    await db.commit()
    await db.refresh(event)
    return result
