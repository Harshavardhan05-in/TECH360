from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.database import Base, engine, async_session_maker
from backend.app.services.region_service import seed_canonical_regions_if_empty
from backend.app.core.seed_data import seed_demo_events_if_empty
from backend.app.core.security import hash_password
from backend.app.models.user import User
from backend.app.models.source import SourceRegistry
from backend.app.models.organizer import Organizer
from backend.app.models.event import Event
from backend.app.models.region import AdministrativeRegion
from backend.app.discovery.scheduler import DiscoveryScheduler

from backend.app.api.routes import health, events, regions, auth, assistant, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eventhorizon")

DEFAULT_SOURCES = [
    {
        "name": "Devpost Hackathons",
        "slug": "devpost",
        "source_type": "platform",
        "base_url": "https://devpost.com/hackathons",
        "feed_url": "https://devpost.com/api/hackathons",
        "crawl_interval_hours": 2,
        "rate_limit_per_min": 20,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "Devfolio Community Hackathons",
        "slug": "devfolio",
        "source_type": "platform",
        "base_url": "https://devfolio.co/hackathons",
        "feed_url": "https://api.devfolio.co/api/hackathons",
        "crawl_interval_hours": 2,
        "rate_limit_per_min": 25,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "Unstop India Competitions",
        "slug": "unstop",
        "source_type": "platform",
        "base_url": "https://unstop.com/hackathons",
        "feed_url": "https://unstop.com/api/public/opportunity/search-result",
        "crawl_interval_hours": 2,
        "rate_limit_per_min": 20,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "FOSS United India Network",
        "slug": "foss-united",
        "source_type": "website",
        "base_url": "https://fossunited.org/events",
        "feed_url": "https://fossunited.org/api/events",
        "crawl_interval_hours": 4,
        "rate_limit_per_min": 20,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "Developer Conferences Global & India",
        "slug": "tech-conferences",
        "source_type": "website",
        "base_url": "https://dev.events/",
        "feed_url": "https://dev.events/rss",
        "crawl_interval_hours": 6,
        "rate_limit_per_min": 15,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "Google Developer Group (GDG) India",
        "slug": "gdg-india",
        "source_type": "website",
        "base_url": "https://gdg.community.dev/events/",
        "feed_url": "https://gdg.community.dev/api/events",
        "crawl_interval_hours": 4,
        "rate_limit_per_min": 15,
        "is_enabled": True,
        "health_status": "healthy"
    },
    {
        "name": "Cybersecurity & CTF Competitions",
        "slug": "cybersecurity-events",
        "source_type": "website",
        "base_url": "https://ctftime.org/event/list/",
        "feed_url": "https://ctftime.org/api/v1/events/",
        "crawl_interval_hours": 6,
        "rate_limit_per_min": 20,
        "is_enabled": True,
        "health_status": "healthy"
    }
]

async def seed_default_sources(db: AsyncSession):
    """Seed verified default sources or add missing ones."""
    for src_data in DEFAULT_SOURCES:
        src_check = await db.execute(select(SourceRegistry).where(SourceRegistry.slug == src_data["slug"]))
        if not src_check.scalar_one_or_none():
            new_src = SourceRegistry(**src_data)
            db.add(new_src)
    await db.commit()

async def init_application_state():
    """Create database tables and seed baseline canonical data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # 1. Seed canonical 28 Indian states + 8 UTs
        await seed_canonical_regions_if_empty(db)

        # 2. Seed initial SuperAdmin account if not existing
        admin_check = await db.execute(select(User).where(User.email == settings.INITIAL_SUPERADMIN_EMAIL))
        if not admin_check.scalar_one_or_none():
            superadmin = User(
                email=settings.INITIAL_SUPERADMIN_EMAIL,
                hashed_password=hash_password(settings.INITIAL_SUPERADMIN_PASSWORD),
                full_name="Platform SuperAdmin",
                role="super_admin",
                is_active=True,
                is_verified=True
            )
            db.add(superadmin)
            await db.commit()
            logger.info("Initialized default superadmin user.")

        # Ensure primary designated administrator account is provisioned
        from backend.scripts.setup_admin import provision_admin
        target_admin_email = os.getenv("ADMIN_EMAIL", "harshavardhan.ushakola14@gmail.com")
        target_admin_pass = os.getenv("ADMIN_PASSWORD", "96325481")
        target_admin_name = os.getenv("ADMIN_NAME", "Harshavardhan Ushakola")
        target_admin_role = os.getenv("ADMIN_ROLE", "admin")
        await provision_admin(target_admin_email, target_admin_pass, target_admin_name, target_admin_role)

        # 3. Seed verified default sources
        await seed_default_sources(db)
        logger.info("Ensured all 7 verified event source registries are registered.")

        # 4. Seed initial events for verification testing
        await seed_demo_events_if_empty(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up EventHorizon AI backend...")
    await init_application_state()
    # Start background hourly discovery cycle
    DiscoveryScheduler.start(interval_seconds=3600)
    yield
    logger.info("Shutting down EventHorizon AI backend...")
    DiscoveryScheduler.stop()

app = FastAPI(
    title=settings.APP_NAME,
    description="Unified AI-Powered Global Tech Event Discovery & Geographic Integrity Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register health check
app.include_router(health.router, prefix="/api")

# Register API v1 routers
app.include_router(events.router, prefix="/api/v1")
app.include_router(regions.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "status": "operational",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
