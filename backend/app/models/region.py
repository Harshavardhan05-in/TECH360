from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

class AdministrativeRegion(Base):
    __tablename__ = "administrative_regions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False) # e.g. IN-TG, IN-KA, IN-DL
    name = Column(String(100), nullable=False)                         # e.g. Telangana, Karnataka
    slug = Column(String(100), unique=True, index=True, nullable=False)# e.g. telangana, karnataka
    type = Column(String(30), nullable=False)                          # state, union_territory, country
    country_code = Column(String(10), default="IN", index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("administrative_regions.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    events = relationship("Event", back_populates="region")
    children = relationship("AdministrativeRegion", backref="parent", remote_side=[id])

    __table_args__ = (
        Index("idx_region_country_type", "country_code", "type"),
    )
