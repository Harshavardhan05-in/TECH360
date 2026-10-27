from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from backend.app.models.region import AdministrativeRegion
from backend.app.models.event import Event
from backend.app.core.canonical_regions import ALL_CANONICAL_INDIAN_REGIONS

async def seed_canonical_regions_if_empty(db: AsyncSession):
    """Seed the 28 Indian States and 8 Union Territories if not already in the database."""
    result = await db.execute(select(func.count(AdministrativeRegion.id)))
    count = result.scalar() or 0
    if count == 0:
        for reg in ALL_CANONICAL_INDIAN_REGIONS:
            region_obj = AdministrativeRegion(
                code=reg["code"],
                name=reg["name"],
                slug=reg["slug"],
                type=reg["type"],
                country_code="IN"
            )
            db.add(region_obj)
        await db.commit()

async def get_all_regions(db: AsyncSession, country_code: str = "IN") -> List[AdministrativeRegion]:
    """Retrieve all administrative regions with event counts."""
    query = select(AdministrativeRegion).where(AdministrativeRegion.country_code == country_code).order_by(AdministrativeRegion.name.asc())
    result = await db.execute(query)
    regions = result.scalars().all()
    return regions

async def get_region_by_slug(db: AsyncSession, slug: str) -> Optional[AdministrativeRegion]:
    """Retrieve a single region by canonical SEO slug."""
    query = select(AdministrativeRegion).where(AdministrativeRegion.slug == slug)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_region_by_code(db: AsyncSession, code: str) -> Optional[AdministrativeRegion]:
    """Retrieve a single region by ISO code (e.g. IN-TG)."""
    query = select(AdministrativeRegion).where(AdministrativeRegion.code == code)
    result = await db.execute(query)
    return result.scalar_one_or_none()
