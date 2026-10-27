from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import List

from backend.app.core.database import get_db
from backend.app.schemas.region import RegionResponse
from backend.app.services.region_service import get_all_regions, get_region_by_slug
from backend.app.models.event import Event
from backend.app.models.region import AdministrativeRegion

router = APIRouter(prefix="/regions", tags=["India & Regions"])

@router.get("", response_model=List[RegionResponse])
async def list_regions(db: AsyncSession = Depends(get_db)):
    """
    List all 28 Indian States and 8 Union Territories with aggregated live event counts.
    """
    regions = await get_all_regions(db)

    # Compute live event counts per region
    counts_query = select(
        Event.region_id,
        func.count(Event.id).label("total_count"),
        func.sum(case((Event.verification_status == "verified", 1), else_=0)).label("verified_count"),
        func.sum(case((Event.verification_status != "verified", 1), else_=0)).label("unverified_count")
    ).group_by(Event.region_id)

    counts_res = await db.execute(counts_query)
    count_map = {row.region_id: row for row in counts_res.all()}

    response_list = []
    for reg in regions:
        c = count_map.get(reg.id)
        response_list.append(
            RegionResponse(
                id=reg.id,
                code=reg.code,
                name=reg.name,
                slug=reg.slug,
                type=reg.type,
                country_code=reg.country_code,
                event_count=c.total_count if c else 0,
                verified_count=c.verified_count if c else 0,
                unverified_count=c.unverified_count if c else 0
            )
        )

    return response_list

@router.get("/{slug}", response_model=RegionResponse)
async def get_region_detail(slug: str, db: AsyncSession = Depends(get_db)):
    """
    Get canonical state or union territory metadata and event totals.
    """
    region = await get_region_by_slug(db, slug)
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrative region '{slug}' not found in canonical Indian registry."
        )

    # Count events for this region
    counts_query = select(
        func.count(Event.id).label("total_count"),
        func.sum(case((Event.verification_status == "verified", 1), else_=0)).label("verified_count"),
        func.sum(case((Event.verification_status != "verified", 1), else_=0)).label("unverified_count")
    ).where(Event.region_id == region.id)

    counts_res = await db.execute(counts_query)
    c = counts_res.one()

    return RegionResponse(
        id=region.id,
        code=region.code,
        name=region.name,
        slug=region.slug,
        type=region.type,
        country_code=region.country_code,
        event_count=c.total_count or 0,
        verified_count=c.verified_count or 0,
        unverified_count=c.unverified_count or 0
    )
