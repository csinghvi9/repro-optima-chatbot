from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    NOT_BOOKED = "not_booked"
    IN_PROCESS = "in_process"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class UserFeedback(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NOT_GIVEN = "not_given"


class User_Info(Document):

    name: Optional[str] = None
    phone_number: Optional[str] = None
    email_id: Optional[str] = None
    pincode: Optional[int] = None
    user_address: Optional[str] = None
    preffered_center_address: Optional[str] = None
    preffered__medical_test: Optional[str] = None
    preffered_ivf_step: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    preffered_center: Optional[list] = []
    checkup_date: Optional[str] = None
    checkup_time_slot: Optional[str] = None
    employment_type: Optional[str] = None
    appointment_status: AppointmentStatus = AppointmentStatus.NOT_BOOKED
    pan_number: Optional[str] = None
    aadhar_number: Optional[int] = None
    user_feedback: UserFeedback = UserFeedback.NOT_GIVEN
    thread_id: str
    crm_api_send: Optional[bool] = False

    class Settings:
        name = "user_information"
