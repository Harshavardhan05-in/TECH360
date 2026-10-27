from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive system health check.
    Pings the database and reports service operational status.
    """
    db_status = "healthy"
    db_latency_ms = 0
    try:
        start = datetime.now(timezone.utc)
        await db.execute(text("SELECT 1"))
        db_latency_ms = round((datetime.now(timezone.utc) - start).total_seconds() * 1000, 2)
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "operational" if db_status == "healthy" else "degraded",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": {
            "status": db_status,
            "latency_ms": db_latency_ms
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
