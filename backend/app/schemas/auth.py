from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    interests: Optional[List[str]] = []
    preferred_formats: Optional[List[str]] = []
    preferred_regions: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserPreferencesUpdate(BaseModel):
    interests: Optional[List[str]] = None
    preferred_formats: Optional[List[str]] = None
    preferred_regions: Optional[List[str]] = None

class SavedEventCreate(BaseModel):
    event_id: int
    notes: Optional[str] = None
    reminder_set: Optional[bool] = False

class SavedEventResponse(BaseModel):
    id: int
    event_id: int
    notes: Optional[str] = None
    reminder_set: bool
    created_at: datetime
    event: Optional[Any] = None # Event response populated by query

    model_config = ConfigDict(from_attributes=True)
