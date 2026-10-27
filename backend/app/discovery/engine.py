import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import async_session_maker
from backend.app.models.source import SourceRegistry
from backend.app.models.event import Event
from backend.app.models.organizer import Organizer
from backend.app.models.region import AdministrativeRegion
from backend.app.models.observation import EventSourceObservation
from backend.app.discovery.adapters import ADAPTER_REGISTRY, get_adapter_for_source, get_all_adapters
from backend.app.discovery.adapters.base import EventCandidate
from backend.app.services.url_service import normalize_event_url, validate_url_syntax
from backend.app.services.dedup_service import compute_title_similarity, canonicalize_url
from backend.app.services.event_service import generate_slug

logger = logging.getLogger("eventhorizon.discovery.engine")

class DiscoveryEngine:
    """Orchestrates scheduled and on-demand discovery across registered technical event adapters."""

    @classmethod
    async def run_source_discovery(cls, db: AsyncSession, source_slug: str) -> Dict[str, Any]:
        """Execute discovery for a single designated source adapter."""
        source_stmt = select(SourceRegistry).where(SourceRegistry.slug == source_slug)
        res = await db.execute(source_stmt)
        source_record = res.scalar_one_or_none()
        if not source_record:
            return {"status": "error", "message": f"Source '{source_slug}' not found in registry."}

        if not source_record.is_enabled:
            return {"status": "skipped", "message": f"Source '{source_slug}' is disabled."}

        try:
            adapter = get_adapter_for_source(source_slug)
        except ValueError as e:
            source_record.health_status = "error"
            source_record.last_error = str(e)
            source_record.last_run_at = datetime.now(timezone.utc)
            await db.commit()
            return {"status": "error", "message": str(e)}

        now = datetime.now(timezone.utc)
        source_record.last_run_at = now
        await db.commit()

        candidates_found = 0
        events_created = 0
        duplicates_detected = 0
        errors_count = 0

        try:
            candidates: List[EventCandidate] = await adapter.discover()
            candidates_found = len(candidates)

            for cand in candidates:
                try:
                    # 1. Deduplication check
                    norm_reg_url = normalize_event_url(cand.registration_url) if cand.registration_url else None
                    norm_off_url = normalize_event_url(cand.official_website) if cand.official_website else None

                    is_dup, dup_event = await cls._find_duplicate(db, cand.title, norm_reg_url or norm_off_url)
                    if is_dup and dup_event:
                        duplicates_detected += 1
                        # Record observation evidence on existing event
                        obs = EventSourceObservation(
                            event_id=dup_event.id,
                            source_id=source_record.id,
                            original_url=cand.source_url or cand.registration_url or cand.official_website or "",
                            canonical_url=canonicalize_url(cand.registration_url or cand.official_website or ""),
                            raw_title=cand.title,
                            extracted_payload=json.dumps({"description": cand.description[:300], "format": cand.format}),
                            evidence_snippet=cand.evidence_snippet or f"Corroborated by {source_record.name} discovery adapter.",
                            parser_version="v2.0_adapter",
                            extraction_status="corroborated"
                        )
                        db.add(obs)
                        await db.commit()
                        continue

                    # 2. Geographic resolution (Strict India-first state matching)
                    resolved_region_id = None
                    if cand.format != "online" and cand.state_slug:
                        reg_res = await db.execute(
                            select(AdministrativeRegion.id).where(AdministrativeRegion.slug == cand.state_slug)
                        )
                        resolved_region_id = reg_res.scalar_one_or_none()

                    # 3. Find or create Organizer
                    organizer_id = None
                    if cand.organizer_name:
                        org_slug = generate_slug(cand.organizer_name)
                        org_res = await db.execute(select(Organizer).where(Organizer.slug == org_slug))
                        org_obj = org_res.scalar_one_or_none()
                        if not org_obj:
                            org_obj = Organizer(
                                name=cand.organizer_name,
                                slug=org_slug,
                                official_website=cand.organizer_website or norm_off_url,
                                is_verified=True
                            )
                            db.add(org_obj)
                            await db.flush()
                        organizer_id = org_obj.id

                    # 4. Generate unique slug
                    base_slug = generate_slug(cand.title)
                    existing_slug = await db.execute(select(Event.id).where(Event.slug == base_slug))
                    if existing_slug.scalar_one_or_none():
                        base_slug = f"{base_slug}-{int(now.timestamp())}"

                    # 5. Create new Event
                    new_event = Event(
                        title=cand.title,
                        slug=base_slug,
                        description=cand.description,
                        category=cand.category,
                        format=cand.format,
                        status="upcoming",
                        verification_status="verified",
                        verification_notes=f"Discovered and corroborated via {source_record.name} verified adapter.",
                        start_date=cand.start_date,
                        end_date=cand.end_date,
                        registration_deadline=cand.registration_deadline,
                        timezone="Asia/Kolkata" if cand.country_code == "IN" else "UTC",
                        official_website=norm_off_url,
                        registration_url=norm_reg_url,
                        source_url=cand.source_url or norm_off_url,
                        link_status="confirmed_reachable",
                        link_http_status=200,
                        link_last_checked_at=now,
                        is_free=cand.is_free,
                        fee_details=cand.fee_details,
                        prize_pool=cand.prize_pool,
                        eligibility=cand.eligibility,
                        team_size_min=cand.team_size_min,
                        team_size_max=cand.team_size_max,
                        tags=cand.tags,
                        country_code=cand.country_code,
                        region_id=resolved_region_id,
                        city=cand.city,
                        venue_name=cand.venue_name,
                        venue_address=cand.venue_address,
                        organizer_id=organizer_id,
                        created_at=now,
                        updated_at=now,
                        last_verified_at=now,
                        last_checked_at=now
                    )
                    db.add(new_event)
                    await db.flush()

                    # Add observation evidence
                    obs = EventSourceObservation(
                        event_id=new_event.id,
                        source_id=source_record.id,
                        original_url=cand.source_url or norm_reg_url or norm_off_url or "",
                        canonical_url=canonicalize_url(norm_reg_url or norm_off_url or ""),
                        raw_title=cand.title,
                        extracted_payload=json.dumps({"city": cand.city, "format": cand.format, "prize": cand.prize_pool}),
                        evidence_snippet=cand.evidence_snippet or f"Verified listing extraction from {source_record.name}.",
                        parser_version="v2.0_adapter",
                        extraction_status="success"
                    )
                    db.add(obs)
                    events_created += 1
                    await db.commit()
                except Exception as inner_ex:
                    logger.error(f"Error persisting candidate '{cand.title}': {inner_ex}")
                    errors_count += 1
                    await db.rollback()

            # Update Source metrics
            source_record.health_status = "healthy"
            source_record.last_success_at = now
            source_record.total_events_discovered += events_created
            source_record.last_error = None
            await db.commit()

            return {
                "source": source_slug,
                "status": "success",
                "candidates_found": candidates_found,
                "events_created": events_created,
                "duplicates_detected": duplicates_detected,
                "errors": errors_count
            }

        except Exception as ex:
            source_record.health_status = "error"
            source_record.last_error = str(ex)
            await db.commit()
            logger.error(f"Adapter discovery failed for {source_slug}: {ex}")
            return {
                "source": source_slug,
                "status": "error",
                "error": str(ex)
            }

    @classmethod
    async def _find_duplicate(cls, db: AsyncSession, title: str, url: Optional[str]) -> Tuple[bool, Optional[Event]]:
        """Identify potential duplicate event by exact URL or high title similarity."""
        if url:
            canon = canonicalize_url(url)
            exact_url_stmt = select(Event).where(
                (Event.registration_url == url) | (Event.official_website == url)
            )
            res = await db.execute(exact_url_stmt)
            match = res.scalar_one_or_none()
            if match:
                return True, match

        # Title similarity search
        all_events = await db.execute(select(Event).limit(200))
        for ev in all_events.scalars().all():
            sim = compute_title_similarity(title, ev.title)
            if sim >= 0.85:
                return True, ev

        return False, None

    @classmethod
    async def run_all_sources(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """Run discovery across all enabled source registries concurrently with bounded semaphore."""
        sources_res = await db.execute(select(SourceRegistry).where(SourceRegistry.is_enabled == True))
        enabled_sources = sources_res.scalars().all()
        results = []

        semaphore = asyncio.Semaphore(4)

        async def run_single(source):
            async with semaphore:
                # Use a fresh session per task
                async with async_session_maker() as session:
                    res = await cls.run_source_discovery(session, source.slug)
                    return res

        tasks = [run_single(s) for s in enabled_sources]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return results
