from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    slug = Column(String(320), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    
    # Classification
    category = Column(String(50), nullable=False, default="hackathon", index=True) # hackathon, conference, workshop, meetup, competition
    format = Column(String(30), nullable=False, default="online", index=True)      # online, in_person, hybrid
    status = Column(String(30), nullable=False, default="upcoming", index=True)    # upcoming, ongoing, completed, cancelled, registration_closed
    verification_status = Column(String(30), nullable=False, default="unverified", index=True) # verified, unverified, needs_review, rejected
    verification_notes = Column(Text, nullable=True) # human or pipeline explanation of verification decision
    
    # Timing
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=True, index=True)
    timezone = Column(String(50), default="Asia/Kolkata", nullable=False)
    
    # URLs & Registration (Separated URL Architecture)
    official_website = Column(String(500), nullable=True) # Official event info / organizer page
    registration_url = Column(String(500), nullable=True) # Direct verified registration link
    source_url = Column(String(1000), nullable=True)      # Original discovered source page
    link_status = Column(String(50), default="unverified", index=True) # confirmed_reachable, redirected, confirmed_not_found, unverified, closed
    link_http_status = Column(Integer, nullable=True)
    link_last_checked_at = Column(DateTime, nullable=True)
    link_error = Column(String(500), nullable=True)
    
    # Costs & Awards
    is_free = Column(Boolean, default=True, index=True)
    fee_details = Column(String(200), nullable=True)
    prize_pool = Column(String(200), nullable=True)
    
    # Participation Criteria
    eligibility = Column(String(300), nullable=True) # e.g. "College Students, Developers", "Open to all"
    team_size_min = Column(Integer, default=1)
    team_size_max = Column(Integer, default=4)
    tags = Column(Text, nullable=True) # Stored as comma-separated or JSON list
    
    # Geographic Resolution (CRITICAL RULES: explicit region FK only for confirmed venues)
    country_code = Column(String(10), default="IN", index=True, nullable=False)
    region_id = Column(Integer, ForeignKey("administrative_regions.id"), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    venue_name = Column(String(300), nullable=True)
    venue_address = Column(String(500), nullable=True)
    
    # Organizer
    organizer_id = Column(Integer, ForeignKey("organizers.id"), nullable=True, index=True)
    
    # Timestamps & Tracking
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_verified_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    region = relationship("AdministrativeRegion", back_populates="events")
    organizer = relationship("Organizer", back_populates="events")
    observations = relationship("EventSourceObservation", back_populates="event", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedEvent", back_populates="event", cascade="all, delete-orphan")
    reports = relationship("EventReport", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_event_category_status", "category", "status"),
        Index("idx_event_geo_format", "region_id", "format"),
        Index("idx_event_deadline", "registration_deadline"),
    )
