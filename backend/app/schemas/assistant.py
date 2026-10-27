from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")

class AssistantQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    messages: Optional[List[ChatMessage]] = Field(default_factory=list, description="Prior conversation messages")
    user_state_preference: Optional[str] = None
    preferred_format: Optional[str] = None

class AssistantEventCitation(BaseModel):
    id: int
    title: str
    slug: str
    category: str
    format: str
    city: Optional[str] = None
    state: Optional[str] = None
    start_date: str
    registration_deadline: Optional[str] = None
    registration_url: Optional[str] = None
    official_website: Optional[str] = None
    is_free: bool
    prize_pool: Optional[str] = None
    verification_status: str

class AssistantQueryResponse(BaseModel):
    answer: str
    events: List[AssistantEventCitation] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
    disclaimer: str = "Recommendations are grounded in verified event records. Check the official registration page for latest updates."
    intent: Optional[str] = None
