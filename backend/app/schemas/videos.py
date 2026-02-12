from pydantic import BaseModel
from app.enum.video import VideoCategory, Languages


class video(BaseModel):

    video_category: VideoCategory = VideoCategory.DOCTOR
    language: Languages = Languages.ENGLISH
    video_heading: str
    video_description: str
    video_number: str
    video_thumbnail: str
