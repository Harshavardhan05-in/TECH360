import asyncio
from backend.app.core.database import async_session_maker
from backend.app.core.seed_data import seed_demo_events_if_empty
from backend.app.services.region_service import seed_canonical_regions_if_empty

async def main():
    async with async_session_maker() as session:
        await seed_canonical_regions_if_empty(session)
        await seed_demo_events_if_empty(session)
    print("Successfully synchronized canonical regions and authentic events.")

if __name__ == "__main__":
    asyncio.run(main())
