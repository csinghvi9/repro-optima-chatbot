from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import PydanticObjectId
from app.models.Commonbase.base import FullyAuditedEntity, BaseDocument


class OtpVerification(FullyAuditedEntity, BaseDocument):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    thread_id: str
    country_code: str = "91"  # Default to India, can be changed if needed
    contact_no: str
    name: str
    otp_code: str
    resend_attempts: int = 0
    max_resend_attempts: int = 3
    is_verified: bool = False
    valid_until: datetime
    resend_cooldown_until: datetime | None = None

    class Settings:
        collection = "otp_verification"
