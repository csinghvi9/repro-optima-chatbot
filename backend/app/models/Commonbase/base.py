from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from beanie import Document, PydanticObjectId
from bson import ObjectId
from app.utils.datetime import utc_now

class BaseDocument(Document):
    def to_json_dict(self):
        result = self.model_dump()
        if hasattr(self, 'id'):
            result["id"] = str(getattr(self, 'id'))

        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, (ObjectId, PydanticObjectId)):
                result[key] = str(value)
        return result

class FullyAuditedEntity(BaseModel):
    created_at: datetime = Field(default_factory=utc_now)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    class Config:
        # Beanie uses Pydantic's base model, so we need to add this config for MongoDB integration
        from_attributes = True


