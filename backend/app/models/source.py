from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class SourceRegistry(Base):
    __tablename__ = "source_registries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    source_type = Column(String(50), nullable=False) # 'platform', 'feed', 'api', 'website'
    base_url = Column(String(500), nullable=False)
    feed_url = Column(String(500), nullable=True)
    crawl_interval_hours = Column(Integer, default=1)
    rate_limit_per_min = Column(Integer, default=30)
    is_enabled = Column(Boolean, default=True)
    
    # Health and monitoring
    health_status = Column(String(30), default="healthy") # healthy, degraded, error
    reliability_score = Column(Float, default=1.0)
    last_run_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error = Column(String(1000), nullable=True)
    total_events_discovered = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    observations = relationship("EventSourceObservation", back_populates="source")
