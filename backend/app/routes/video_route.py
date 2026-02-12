from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError
from app.auth.auth import get_admin_user
from app.schemas.videos import video
from app.cruds.video_cruds import create_video_entry


router = APIRouter()


@router.post("/create_videos_details")
async def create_videos_details(
    video_detail: video, current_user: dict = Depends(get_admin_user)
):
    try:
        video_data = await create_video_entry(video_detail)
        return {"message": "Video Entry created successfully", "video": video_data}
    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating thread",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating thread",
        )
