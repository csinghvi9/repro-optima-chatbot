from beanie import Document
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
from app.models.message import Message


class Cache(BaseModel):
    city: Optional[str] = ""
    intent: Optional[str] = ""
    preferred_center: Optional[str] = ""
    need_type: Optional[str] = ""
    faq_count: int = 0
    center_lookup_count: int = 0
    lead_generation: int = 0
    resend: int = 00000
    clarification: int = 0


class Thread(Document):
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc))
    thread_name: Optional[str] = None
    user_id: str
    language: Optional[str] = None
    flow_id: Optional[str] = None
    step_id: Optional[str] = None
    previous_flow: Optional[str] = None
    previous_step: Optional[str] = None
    step_count: Optional[int] = 0
    location: Optional[str] = ""
    country: Optional[str] = ""
    messages: Optional[list[Message]] = Field(default_factory=list)
    cache: Optional[Cache] = Field(default_factory=Cache)
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-04-10T15:22:45.123Z",
                "thread_name": "example",
                "user_id": "abcdhnwiubfi",
                "location": "Delhi",
                "country": "India",
                "cache": {
                    "city": "Delhi",
                    "intent": "lead_generation",
                    "preferred_center": "IVF Delhi",
                    "need_type": "IVF",
                    "faq_count": 0,
                    "center_lookup_count": 1,
                    "lead_generation": 1,
                    "resend": 0,
                    "clarification": 0,
                },
            }
        }

    class Settings:
        name = "threads"
