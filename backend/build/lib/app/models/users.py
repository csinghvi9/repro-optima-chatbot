from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from app.enum.role_enum import RoleName


class User(Document):

    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role_name: RoleName = RoleName.ADMIN

    class Settings:
        name = "users"
