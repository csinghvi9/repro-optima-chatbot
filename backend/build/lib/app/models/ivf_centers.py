from beanie import Document
from typing import Optional


class IVF_Center(Document):

    Pincode: Optional[int] = 0
    Latitude: Optional[float] = 0
    Longitude: Optional[float] = 0
    Tehsil: Optional[str] = None
    District: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None

    class Settings:
        name = "IVFCenters"
