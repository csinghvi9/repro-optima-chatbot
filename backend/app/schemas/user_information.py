from pydantic import BaseModel, EmailStr
from typing import Optional


class UserInformation(BaseModel):
    firstName: str
    mobile: str
    email: Optional[str] = None
    employmentType: Optional[str] = None
    address: Optional[str] = None
    treatmentLocation: Optional[str] = None
    pincode: Optional[int] = None
    state: Optional[str] = None
    pan: Optional[str] = None
    aadhar: Optional[int] = None
