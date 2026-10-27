from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from backend.app.schemas.region import RegionResponse

class OrganizerBrief(BaseModel):
    id: int
    name: str
    slug: str
    official_website: Optional[str] = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)

class ObservationBrief(BaseModel):
    id: int
    source_name: Optional[str] = None
    original_url: str
    canonical_url: str
    observed_at: datetime
    evidence_snippet: Optional[str] = None
    parser_version: str

    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    description: str
    category: str = "hackathon"
    format: str = "online" # online, in_person, hybrid
    status: str = "upcoming"
    verification_status: str = "unverified"
    verification_notes: Optional[str] = None
    
    start_date: datetime
    end_date: datetime
    registration_deadline: Optional[datetime] = None
    timezone: str = "Asia/Kolkata"
    
    official_website: Optional[str] = None
    registration_url: Optional[str] = None
    source_url: Optional[str] = None
    link_status: Optional[str] = "unverified"
    link_http_status: Optional[int] = None
    link_error: Optional[str] = None
    
    is_free: bool = True
    fee_details: Optional[str] = None
    prize_pool: Optional[str] = None
    eligibility: Optional[str] = None
    team_size_min: Optional[int] = 1
    team_size_max: Optional[int] = 4
    tags: Optional[str] = None
    
    country_code: str = "IN"
    region_id: Optional[int] = None
    city: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None

class EventCreate(EventBase):
    organizer_id: Optional[int] = None
    organizer_name: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    verification_status: Optional[str] = None
    verification_notes: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    timezone: Optional[str] = None
    official_website: Optional[str] = None
    registration_url: Optional[str] = None
    source_url: Optional[str] = None
    link_status: Optional[str] = "unverified"
    link_http_status: Optional[int] = None
    link_error: Optional[str] = None
    is_free: Optional[bool] = None
    fee_details: Optional[str] = None
    prize_pool: Optional[str] = None
    eligibility: Optional[str] = None
    team_size_min: Optional[int] = None
    team_size_max: Optional[int] = None
    tags: Optional[str] = None
    country_code: Optional[str] = None
    region_id: Optional[int] = None
    city: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    organizer_id: Optional[int] = None

class EventResponse(EventBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime
    last_verified_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    
    region: Optional[RegionResponse] = None
    organizer: Optional[OrganizerBrief] = None
    observations: List[ObservationBrief] = []
    is_saved: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class EventListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[EventResponse]

class EventReportCreate(BaseModel):
    reporter_email: Optional[str] = None
    issue_type: str # wrong_location, incorrect_date, broken_link, expired
    description: str

class EventReportResponse(BaseModel):
    id: int
    event_id: int
    issue_type: str
    description: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
