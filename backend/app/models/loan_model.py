from beanie import Document
from typing import Optional


class Loan_User(Document):

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
    thread_id: str
    reference_id: str

    class Settings:
        name = "loan_user"
