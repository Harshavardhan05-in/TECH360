from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse
from backend.app.services.assistant_service import execute_assistant_query

router = APIRouter(prefix="/assistant", tags=["AI Event Assistant"])

@router.post("/query", response_model=AssistantQueryResponse)
async def query_assistant(
    payload: AssistantQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Query the ground-truth AI Event Assistant.
    Retrieves authentic database records and structures verified links and deadlines.
    Guarantees no fabricated events, links, or dates.
    """
    response = await execute_assistant_query(db, payload)
    return response
