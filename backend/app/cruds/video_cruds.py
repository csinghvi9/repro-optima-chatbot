from app.schemas.videos import video
from app.models.videos import Video
from fastapi import HTTPException, status


async def create_video_entry(video_detail: video):
    try:
        videos = Video(
            video_category=video_detail.video_category,
            language=video_detail.language,
            video_heading=video_detail.video_heading,
            video_description=video_detail.video_description,
            video_number=video_detail.video_number,
            video_thumbnail=video_detail.video_thumbnail,
        )
        await videos.insert()
        return videos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating video",
        )
