from pydantic import BaseModel, EmailStr
from typing import Optional


class LoanUserInformation(BaseModel):
    name: str
    phone_number: str
    email_id: Optional[str] = None
    pincode: Optional[int] = None
    user_address: Optional[str] = None
    employment_type: Optional[str] = None
    state: Optional[str] = None
    treatment_location: Optional[str] = None
    pan_number: str
    aadhar_number: int
