from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class EventSourceObservation(Base):
    __tablename__ = "event_source_observations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("source_registries.id"), nullable=True, index=True)
    
    # Raw source URL and normalized canonical URL
    original_url = Column(String(1000), nullable=False)
    canonical_url = Column(String(1000), nullable=False, index=True)
    raw_title = Column(String(500), nullable=False)
    
    # Extracted data payload (JSON serialized string)
    extracted_payload = Column(Text, nullable=False)
    evidence_snippet = Column(Text, nullable=True)
    parser_version = Column(String(50), default="v1.0")
    extraction_status = Column(String(50), default="success") # success, partial, failed
    
    observed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    event = relationship("Event", back_populates="observations")
    source = relationship("SourceRegistry", back_populates="observations")

    __table_args__ = (
        Index("idx_observation_canonical", "canonical_url"),
    )
