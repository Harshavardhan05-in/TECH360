import math
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from backend.app.core.database import get_db
from backend.app.schemas.event import EventResponse, EventListResponse, EventReportCreate, EventReportResponse
from backend.app.services.event_service import get_events, get_event_by_id_or_slug, report_event, check_and_update_event_link
from backend.app.services.auth_service import track_anonymous_event_view
from backend.app.api.deps import get_client_ip, get_current_user_optional
from backend.app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/parse-query")
async def parse_query_endpoint(
    q: str = Query(..., description="Natural language search expression")
):
    """Parse natural language query into validated structured filters and keyword terms."""
    from backend.app.services.search_service import parse_natural_language_search
    return parse_natural_language_search(q)

@router.get("", response_model=EventListResponse)
async def list_events(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search by keywords, title, city, or tags"),
    category: Optional[str] = Query(None, description="Category filter (hackathon, conference, workshop, meetup)"),
    format: Optional[str] = Query(None, description="Format filter (online, in_person, hybrid)"),
    status: Optional[str] = Query(None, description="Status filter (upcoming, ongoing, completed)"),
    verification_status: Optional[str] = Query(None, description="Verification status (verified, unverified, needs_review)"),
    country_code: Optional[str] = Query(None, description="Country filter (e.g. IN)"),
    state_slug: Optional[str] = Query(None, description="Canonical Indian state slug (e.g. telangana, karnataka)"),
    region_id: Optional[int] = Query(None, description="Direct region ID"),
    is_free: Optional[bool] = Query(None, description="Free entry filter"),
    include_online: bool = Query(False, description="When viewing a state, include online events accessible from anywhere"),
    sort_by: str = Query("start_date", description="Sort field: start_date, deadline, created_at"),
    date_preset: Optional[str] = Query(None, description="Date filter preset: today, this_week, this_month, next_30_days, next_90_days"),
    start_date_gte: Optional[str] = Query(None, description="ISO datetime/date string for start date lower bound"),
    start_date_lte: Optional[str] = Query(None, description="ISO datetime/date string for start date upper bound"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search and filter events with strict geographic integrity.
    """
    # Parse date strings if supplied
    from datetime import datetime
    gte_dt = None
    lte_dt = None
    if start_date_gte:
        try:
            gte_dt = datetime.fromisoformat(start_date_gte.replace("Z", "+00:00"))
        except ValueError:
            pass
    if start_date_lte:
        try:
            lte_dt = datetime.fromisoformat(start_date_lte.replace("Z", "+00:00"))
        except ValueError:
            pass

    events, total = await get_events(
        db=db,
        page=page,
        page_size=page_size,
        query=q,
        category=category,
        format=format,
        status=status,
        verification_status=verification_status,
        country_code=country_code,
        state_slug=state_slug,
        region_id=region_id,
        is_free=is_free,
        include_online_in_state=include_online,
        sort_by=sort_by,
        date_preset=date_preset,
        start_date_gte=gte_dt,
        start_date_lte=lte_dt
    )

    pages = math.ceil(total / page_size) if total > 0 else 1

    return EventListResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        items=events
    )

@router.get("/{identifier}", response_model=EventResponse)
async def get_event_detail(
    identifier: str,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve full event details and observation evidence.
    Enforces the server-side 5-view browsing limit for anonymous visitors.
    """
    event = await get_event_by_id_or_slug(db, identifier)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{identifier}' was not found or has been removed."
        )

    # If user is anonymous, check view allowance
    if not current_user:
        client_ip = get_client_ip(request)
        allowed, views_used, limit = track_anonymous_event_view(client_ip, event.id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "You have reached your 5 free event views limit. Create a free account or sign in to continue viewing event details.",
                    "view_limit_reached": True,
                    "views_used": views_used,
                    "limit": limit
                }
            )

    return event

@router.post("/{event_id}/report", response_model=EventReportResponse)
async def submit_event_report(
    event_id: int,
    payload: EventReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """Submit a report for incorrect dates, location, or broken registration links."""
    event = await get_event_by_id_or_slug(db, str(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    report = await report_event(db, event_id, payload)
    return report

@router.post("/{event_id}/verify-link")
async def verify_single_event_link(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Controlled backend validation checking if the event registration destination is reachable."""
    result = await check_and_update_event_link(db, event_id)
    return result
