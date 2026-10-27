import asyncio
import logging
from datetime import datetime, timezone
from backend.app.core.database import async_session_maker
from backend.app.discovery.engine import DiscoveryEngine

logger = logging.getLogger("eventhorizon.discovery.scheduler")

class DiscoveryScheduler:
    """Background periodic discovery scheduler running hourly cycles."""

    _task: asyncio.Task = None
    _is_running: bool = False
    _interval_seconds: int = 3600 # 1 hour

    @classmethod
    def start(cls, interval_seconds: int = 3600):
        if cls._is_running:
            return
        cls._is_running = True
        cls._interval_seconds = interval_seconds
        cls._task = asyncio.create_task(cls._run_loop())
        logger.info(f"DiscoveryScheduler started with interval={interval_seconds}s")

    @classmethod
    def stop(cls):
        if cls._task and not cls._task.done():
            cls._task.cancel()
        cls._is_running = False
        logger.info("DiscoveryScheduler stopped.")

    @classmethod
    async def _run_loop(cls):
        # Initial brief delay to let application start up cleanly
        await asyncio.sleep(5)
        while cls._is_running:
            try:
                logger.info("DiscoveryScheduler: Starting scheduled discovery cycle across enabled sources...")
                async with async_session_maker() as session:
                    results = await DiscoveryEngine.run_all_sources(session)
                    logger.info(f"DiscoveryScheduler cycle finished: {len(results)} sources processed.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"DiscoveryScheduler cycle encountered error: {e}")

            # Sleep until next cycle
            try:
                await asyncio.sleep(cls._interval_seconds)
            except asyncio.CancelledError:
                break
