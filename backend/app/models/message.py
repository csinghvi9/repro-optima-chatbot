from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional, Union, Any
from beanie import Document


class Message(Document):
    content: Any
    role: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    contentType: Optional[str] = None
    flow_id: Optional[str] = None
