import json
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.schemas.admin import (
    AdminStatsResponse, BulkDeleteRequest, SourceResponse,
    SourceCreate, SourceUpdate, AuditLogResponse
)
from backend.app.schemas.event import EventCreate, EventUpdate, EventResponse
from backend.app.services.event_service import create_event, update_event, delete_event
from backend.app.api.deps import require_role, get_current_user, get_client_ip
from backend.app.models.user import User
from backend.app.models.event import Event
from backend.app.models.source import SourceRegistry
from backend.app.models.saved_event import AuditLog, EventReport

router = APIRouter(prefix="/admin", tags=["Administration & Operations"])

async def record_audit_log(
    db: AsyncSession,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    details: dict,
    ip_address: Optional[str] = None
):
    """Write an immutable audit log entry."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details),
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc)
    )
    db.add(entry)
    await db.commit()

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_metrics(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    Compute real operational metrics directly from live database tables.
    Never returns hardcoded or fabricated statistics.
    """
    now = datetime.now(timezone.utc)

    # Event metrics
    total_events_res = await db.execute(select(func.count(Event.id)))
    total_events = total_events_res.scalar() or 0

    verified_res = await db.execute(select(func.count(Event.id)).where(Event.verification_status == "verified"))
    verified_events = verified_res.scalar() or 0

    unverified_res = await db.execute(select(func.count(Event.id)).where(Event.verification_status == "unverified"))
    unverified_events = unverified_res.scalar() or 0

    review_res = await db.execute(select(func.count(Event.id)).where(Event.verification_status == "needs_review"))
    needs_review = review_res.scalar() or 0

    upcoming_res = await db.execute(select(func.count(Event.id)).where(Event.start_date >= now))
    upcoming_events = upcoming_res.scalar() or 0

    expired_res = await db.execute(select(func.count(Event.id)).where(Event.end_date < now))
    expired_events = expired_res.scalar() or 0

    # Source metrics
    total_sources_res = await db.execute(select(func.count(SourceRegistry.id)))
    total_sources = total_sources_res.scalar() or 0

    error_sources_res = await db.execute(select(func.count(SourceRegistry.id)).where(SourceRegistry.health_status == "error"))
    error_sources = error_sources_res.scalar() or 0

    # Pending reports
    reports_res = await db.execute(select(func.count(EventReport.id)).where(EventReport.status == "pending"))
    pending_reports = reports_res.scalar() or 0

    # User count
    users_res = await db.execute(select(func.count(User.id)))
    total_users = users_res.scalar() or 0

    return AdminStatsResponse(
        total_published_events=total_events,
        verified_events=verified_events,
        unverified_events=unverified_events,
        needs_review_events=needs_review,
        upcoming_events=upcoming_events,
        expired_or_closed_events=expired_events,
        total_sources=total_sources,
        sources_with_errors=error_sources,
        pending_reports=pending_reports,
        total_users=total_users
    )

@router.post("/events", response_model=EventResponse)
async def admin_create_event(
    payload: EventCreate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Manually add a verified or reviewed event listing."""
    event = await create_event(db, payload)
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="EVENT_MANUAL_CREATE",
        resource_type="event",
        resource_id=str(event.id),
        details={"title": event.title, "verification_status": event.verification_status},
        ip_address=get_client_ip(request)
    )
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
async def admin_update_event(
    event_id: int,
    payload: EventUpdate,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Update event fields, modify verification status, or correct geographic classification."""
    updated = await update_event(db, event_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found.")

    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="EVENT_ADMIN_UPDATE",
        resource_type="event",
        resource_id=str(event_id),
        details=payload.model_dump(exclude_unset=True),
        ip_address=get_client_ip(request)
    )
    return updated

@router.delete("/events/{event_id}")
async def admin_delete_single_event(
    event_id: int,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Delete an individual event listing."""
    success = await delete_event(db, event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found.")

    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="EVENT_SINGLE_DELETE",
        resource_type="event",
        resource_id=str(event_id),
        details={"deleted_event_id": event_id},
        ip_address=get_client_ip(request)
    )
    return {"message": f"Event {event_id} deleted."}

@router.get("/sources", response_model=List[SourceResponse])
async def list_sources(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Inspect all registered discovery sources and their health metrics."""
    result = await db.execute(select(SourceRegistry).order_by(SourceRegistry.id.asc()))
    return result.scalars().all()

@router.post("/sources", response_model=SourceResponse)
async def add_source(
    payload: SourceCreate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Register a new discovery feed or API source."""
    slug = payload.name.lower().replace(" ", "-")
    source = SourceRegistry(
        name=payload.name,
        slug=slug,
        source_type=payload.source_type,
        base_url=payload.base_url,
        feed_url=payload.feed_url,
        crawl_interval_hours=payload.crawl_interval_hours,
        rate_limit_per_min=payload.rate_limit_per_min,
        is_enabled=True,
        health_status="healthy",
        created_at=datetime.now(timezone.utc)
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source

@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    payload: SourceUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Enable/disable a source or adjust rate limits."""
    result = await db.execute(select(SourceRegistry).where(SourceRegistry.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found.")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(source, k, v)

    await db.commit()
    await db.refresh(source)
    return source

@router.post("/bulk-delete")
async def bulk_delete_events(
    payload: BulkDeleteRequest,
    request: Request,
    current_user: User = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """
    CRITICAL HIGH-RISK ADMINISTRATIVE ACTION:
    Deletes event records only when authorized by SUPER_ADMIN and verified with
    the exact required typed confirmation phrase: 'DELETE ALL EVENTS PERMANENTLY'.
    Leaves source registries, user accounts, and system configuration intact.
    Logs an immutable security audit entry.
    """
    REQUIRED_PHRASE = "DELETE ALL EVENTS PERMANENTLY"
    if payload.confirmation_phrase.strip() != REQUIRED_PHRASE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Typed confirmation phrase mismatch. Must match exactly: '{REQUIRED_PHRASE}'"
        )

    if payload.scope == "all":
        # Count events before deleting
        count_res = await db.execute(select(func.count(Event.id)))
        count = count_res.scalar() or 0
        await db.execute(delete(Event))
        await db.commit()
    elif payload.scope == "unverified":
        count_res = await db.execute(select(func.count(Event.id)).where(Event.verification_status != "verified"))
        count = count_res.scalar() or 0
        await db.execute(delete(Event).where(Event.verification_status != "verified"))
        await db.commit()
    else:
        raise HTTPException(status_code=400, detail="Invalid deletion scope.")

    # Record critical audit log
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="CRITICAL_BULK_DELETE",
        resource_type="events",
        resource_id=None,
        details={
            "scope": payload.scope,
            "events_deleted": count,
            "initiated_by": current_user.email
        },
        ip_address=get_client_ip(request)
    )

    return {
        "status": "success",
        "message": f"Successfully deleted {count} event(s) under scope '{payload.scope}'.",
        "deleted_count": count
    }

@router.post("/discovery/run")
async def trigger_full_discovery(
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Admin-triggered discovery run across all enabled source adapters."""
    from backend.app.discovery.engine import DiscoveryEngine
    results = await DiscoveryEngine.run_all_sources(db)
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="DISCOVERY_BATCH_RUN",
        resource_type="discovery",
        resource_id=None,
        details={"results": results},
        ip_address=get_client_ip(request)
    )
    return {"status": "success", "summary": results}

@router.post("/discovery/sources/{slug}/run")
async def trigger_source_discovery(
    slug: str,
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Admin-triggered discovery run for a specific adapter."""
    from backend.app.discovery.engine import DiscoveryEngine
    result = await DiscoveryEngine.run_source_discovery(db, slug)
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="DISCOVERY_SINGLE_SOURCE_RUN",
        resource_type="source",
        resource_id=slug,
        details=result,
        ip_address=get_client_ip(request)
    )
    return result

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve security and administrative audit logs."""
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    return result.scalars().all()
