from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class SavedEvent(Base):
    __tablename__ = "saved_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    reminder_set = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="saved_events")
    event = relationship("Event", back_populates="saved_by_users")

    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event_save"),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False) # e.g. "EVENT_CREATED", "LOCATION_CORRECTED", "BULK_DELETE"
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True) # JSON details before/after
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="audit_logs")

class EventReport(Base):
    __tablename__ = "event_reports"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    reporter_email = Column(String(255), nullable=True)
    issue_type = Column(String(100), nullable=False) # "wrong_location", "incorrect_date", "broken_link", "expired"
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending") # pending, reviewed, resolved, rejected
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="reports")
