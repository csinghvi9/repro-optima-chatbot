from pydantic import BaseModel, Field, constr
from typing import Annotated, Optional
from datetime import datetime

OtpCode = Annotated[str, constr(min_length=6, max_length=6, pattern=r"^\d{6}$")]


class OtpVerificationBase(BaseModel):
    country_code: Optional[str] = Field(
        default="91", description="Country code, defaults to '91' for India"
    )
    contact_no: str
    name: Optional[str] = None


class OtpRequest(OtpVerificationBase):
    pass


class OtpVerify(OtpVerificationBase):
    otp_code: OtpCode


class OtpVerificationOut(OtpVerificationBase):
    id: str
    otp_code: str
    resend_attempts: int
    max_resend_attempts: int
    is_verified: bool
    session_id: str
    valid_until: datetime
    resend_cooldown_until: Optional[datetime] = None

    class Config:
        # This excludes the 'otp_code' field from being included in the response
        exclude = {"otp_code"}
