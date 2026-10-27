import json
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.app.core.database import get_db
from backend.app.core.security import create_access_token
from backend.app.schemas.auth import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    UserPreferencesUpdate, SavedEventCreate, SavedEventResponse
)
from backend.app.services.auth_service import (
    register_user, authenticate_user, update_preferences,
    save_event, unsave_event, get_saved_events
)
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication & Personalization"])

def build_user_response(user: User) -> UserResponse:
    interests = []
    preferred_formats = []
    preferred_regions = []
    if user.preferences:
        try:
            interests = json.loads(user.preferences.interests or "[]")
            preferred_formats = json.loads(user.preferences.preferred_formats or "[]")
            preferred_regions = json.loads(user.preferences.preferred_regions or "[]")
        except Exception:
            pass

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        interests=interests,
        preferred_formats=preferred_formats,
        preferred_regions=preferred_regions
    )

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    """Register a new developer account and return session token."""
    user, error = await register_user(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=build_user_response(user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password."""
    user, error = await authenticate_user(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=build_user_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get authenticated user profile and saved interests."""
    return build_user_response(current_user)

@router.put("/preferences", response_model=UserResponse)
async def update_user_preferences(
    payload: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user personalization preferences (domains, formats, regions)."""
    await update_preferences(db, current_user.id, payload)
    # Reload user
    return build_user_response(current_user)

@router.get("/saved-events")
async def list_saved_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all bookmarked events for authenticated user."""
    saved_items = await get_saved_events(db, current_user.id)
    results = []
    for item in saved_items:
        results.append({
            "id": item.id,
            "event_id": item.event_id,
            "notes": item.notes,
            "reminder_set": item.reminder_set,
            "created_at": item.created_at,
            "event": item.event
        })
    return results

@router.post("/saved-events")
async def add_saved_event(
    payload: SavedEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bookmark an event."""
    saved, error = await save_event(db, current_user.id, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"message": "Event saved successfully.", "saved_id": saved.id}

@router.delete("/saved-events/{event_id}")
async def remove_saved_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a bookmarked event."""
    removed = await unsave_event(db, current_user.id, event_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found.")
    return {"message": "Bookmark removed."}
