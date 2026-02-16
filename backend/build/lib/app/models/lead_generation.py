# schemas/ivf.py or wherever you manage request schemas
from pydantic import BaseModel, Field
from typing import Optional


class IVFLeadCreationRequest(BaseModel):
    full_name: str
    contact_no: str
    pincode: Optional[str] = Field(default="580024", example="580024")
