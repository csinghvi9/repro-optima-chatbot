from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional
from app.enum.video import VideoCategory, Languages


class Video(Document):

    video_category: VideoCategory = VideoCategory.DOCTOR
    language: Languages = Languages.ENGLISH
    video_heading: str
    video_description: str
    video_number: str
    video_thumbnail: str

    class Settings:
        name = "videos"
