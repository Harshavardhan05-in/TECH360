from pydantic import BaseModel, ConfigDict
from typing import Optional

class RegionBase(BaseModel):
    code: str
    name: str
    slug: str
    type: str
    country_code: str = "IN"

class RegionResponse(RegionBase):
    id: int
    event_count: Optional[int] = 0
    verified_count: Optional[int] = 0
    unverified_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
