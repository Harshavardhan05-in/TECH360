from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class BulkDeleteRequest(BaseModel):
    confirmation_phrase: str = Field(..., description="Must match: DELETE ALL EVENTS PERMANENTLY")
    scope: str = "unverified" # 'all' or 'unverified' or 'expired'

class AdminStatsResponse(BaseModel):
    total_published_events: int
    verified_events: int
    unverified_events: int
    needs_review_events: int
    upcoming_events: int
    expired_or_closed_events: int
    total_sources: int
    sources_with_errors: int
    pending_reports: int
    total_users: int

class SourceResponse(BaseModel):
    id: int
    name: str
    slug: str
    source_type: str
    base_url: str
    feed_url: Optional[str] = None
    crawl_interval_hours: int
    rate_limit_per_min: int
    is_enabled: bool
    health_status: str
    reliability_score: float
    last_run_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    total_events_discovered: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SourceCreate(BaseModel):
    name: str
    source_type: str = "feed" # platform, feed, api, website
    base_url: str
    feed_url: Optional[str] = None
    crawl_interval_hours: int = 1
    rate_limit_per_min: int = 30

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    is_enabled: Optional[bool] = None
    crawl_interval_hours: Optional[int] = None
    rate_limit_per_min: Optional[int] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
