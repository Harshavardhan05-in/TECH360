import json
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.config import settings
from backend.app.models.user import User, UserPreference
from backend.app.models.saved_event import SavedEvent
from backend.app.models.event import Event
from backend.app.schemas.auth import UserRegister, UserLogin, UserPreferencesUpdate, SavedEventCreate

# Server-side in-memory view tracker for anonymous visitors:
# Maps client_ip -> set of viewed unique event_ids
_ANONYMOUS_VIEW_STORE: Dict[str, Set[int]] = {}

def reset_anonymous_view_store():
    """Reset anonymous view tracker for tests."""
    _ANONYMOUS_VIEW_STORE.clear()

def track_anonymous_event_view(client_ip: str, event_id: int) -> Tuple[bool, int, int]:
    """
    Tracks anonymous visitor event detail views.
    Returns: (is_allowed, views_used, limit).
    Counts unique event detail views to avoid penalizing refreshes on the same event.
    """
    limit = settings.ANONYMOUS_EVENT_VIEW_LIMIT
    if client_ip not in _ANONYMOUS_VIEW_STORE:
        _ANONYMOUS_VIEW_STORE[client_ip] = set()

    viewed_events = _ANONYMOUS_VIEW_STORE[client_ip]
    
    # If user has already viewed this event, allow re-viewing without decrementing allowance
    if event_id in viewed_events:
        return True, len(viewed_events), limit
    
    # Check if they have reached or exceeded the limit
    if len(viewed_events) >= limit:
        return False, len(viewed_events), limit

    # Register new unique view
    viewed_events.add(event_id)
    return True, len(viewed_events), limit

async def register_user(db: AsyncSession, payload: UserRegister) -> Tuple[Optional[User], Optional[str]]:
    """Register a new user account with hashed password and initial preferences."""
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        return None, "An account with this email already exists."

    hashed = hash_password(payload.password)
    user = User(
        email=payload.email.lower(),
        hashed_password=hashed,
        full_name=payload.full_name,
        role="user",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    await db.flush()

    # Create empty preferences
    pref = UserPreference(
        user_id=user.id,
        interests=json.dumps([]),
        preferred_formats=json.dumps([]),
        preferred_regions=json.dumps([])
    )
    db.add(pref)
    await db.commit()

    # Re-fetch user with loaded preferences to prevent async relationship detachment
    user_stmt = select(User).options(selectinload(User.preferences)).where(User.id == user.id)
    refreshed_user = (await db.execute(user_stmt)).scalar_one()
    return refreshed_user, None

async def authenticate_user(db: AsyncSession, payload: UserLogin) -> Tuple[Optional[User], Optional[str]]:
    """Verify user credentials and return authenticated user."""
    result = await db.execute(select(User).options(selectinload(User.preferences)).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        return None, "Invalid email or password."
    if not user.is_active:
        return None, "This account is inactive. Please contact support."
    return user, None

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Retrieve user with loaded preferences."""
    result = await db.execute(select(User).options(selectinload(User.preferences)).where(User.id == user_id))
    return result.scalar_one_or_none()

async def update_preferences(db: AsyncSession, user_id: int, payload: UserPreferencesUpdate) -> Optional[UserPreference]:
    """Update user preference tags, formats, and regions."""
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user_id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=user_id)
        db.add(pref)

    if payload.interests is not None:
        pref.interests = json.dumps(payload.interests)
    if payload.preferred_formats is not None:
        pref.preferred_formats = json.dumps(payload.preferred_formats)
    if payload.preferred_regions is not None:
        pref.preferred_regions = json.dumps(payload.preferred_regions)

    pref.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(pref)
    return pref

async def save_event(db: AsyncSession, user_id: int, payload: SavedEventCreate) -> Tuple[Optional[SavedEvent], Optional[str]]:
    """Save an event for a user with duplicate prevention."""
    # Check if already saved
    existing = await db.execute(select(SavedEvent).where(and_(SavedEvent.user_id == user_id, SavedEvent.event_id == payload.event_id)))
    if existing.scalar_one_or_none():
        return None, "Event is already saved."

    # Check if event exists
    event = await db.execute(select(Event.id).where(Event.id == payload.event_id))
    if not event.scalar_one_or_none():
        return None, "Event does not exist."

    saved = SavedEvent(
        user_id=user_id,
        event_id=payload.event_id,
        notes=payload.notes,
        reminder_set=payload.reminder_set or False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved, None

async def unsave_event(db: AsyncSession, user_id: int, event_id: int) -> bool:
    """Remove a saved event bookmark."""
    result = await db.execute(select(SavedEvent).where(and_(SavedEvent.user_id == user_id, SavedEvent.event_id == event_id)))
    saved = result.scalar_one_or_none()
    if not saved:
        return False
    await db.delete(saved)
    await db.commit()
    return True

async def get_saved_events(db: AsyncSession, user_id: int) -> List[SavedEvent]:
    """Retrieve all saved events for user, including populated event records."""
    stmt = select(SavedEvent).options(
        selectinload(SavedEvent.event).selectinload(Event.region),
        selectinload(SavedEvent.event).selectinload(Event.organizer)
    ).where(SavedEvent.user_id == user_id).order_by(SavedEvent.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()
