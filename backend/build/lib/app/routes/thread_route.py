from fastapi import APIRouter, HTTPException, Depends, status
from app.models.threads import Thread
from datetime import datetime, timezone, timedelta
from pymongo.errors import PyMongoError
from app.auth.auth import get_current_user, get_admin_user
from app.auth.jwt_handler import update_jwt
from app.cruds.threads_cruds import (
    delete_thread,
    update_thread_name,
    convert_objectid_to_str,
)
from app.schemas.thread_schemas import ThreadEditRequest
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
import traceback
from fastapi.encoders import jsonable_encoder

router = APIRouter()


# class ThreadEditRequest(BaseModel):
#     name: str
#     thread_id: str


class ChangeLangRequest(BaseModel):
    thread_id: str
    language: str


@router.delete("/delete_thread")
async def delete_threadd(
    thread_id: str, current_user: dict = Depends(get_current_user)
):
    try:
        if not thread_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Thread ID is required",
            )

        respone = await delete_thread(thread_id)
        return {"response": respone}

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error while deleting thread"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while deleting thread"
        )


@router.post("/edit_name")
async def edit_name(
    request: ThreadEditRequest, current_user: dict = Depends(get_current_user)
):
    try:
        if not request.thread_id:
            raise HTTPException(
                status_code=400, detail="Thread ID is missing or invalid"
            )

        response = await update_thread_name(request.thread_id, request.name)
        if response:
            return {"response": "Name edited Successfully"}
        raise HTTPException(status_code=400, detail="Name not edited")
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating thread name",
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while editing thread name",
        )


@router.get("/get_threads")
async def get_threads(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    thread_id: Optional[str] = None,
    current_user: dict = Depends(get_admin_user),
):
    try:
        if thread_id:
            pipeline = [
                {"$addFields": {"id_str": {"$toString": "$_id"}}},
                {"$match": {"id_str": {"$regex": thread_id}}},
                {"$sort": {"timestamp": -1}},
            ]
            cursor = Thread.get_pymongo_collection().aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return {"threads": convert_objectid_to_str(results)}

        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ) + timedelta(days=1)

            threads = await Thread.find(
                {"timestamp": {"$gte": start, "$lt": end}}
            ).to_list()

            threads = sorted(threads, key=lambda x: x.timestamp, reverse=True)
            return {"threads": threads}

        return {"threads": []}

    except Exception:
        traceback.print_exc()
        raise HTTPException(500, "Failed to fetch threads")


@router.get("/create_threads")
async def create_thread(lang: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing or invalid")

        new_thread = Thread(
            user_id=user_id,
            thread_name="New Chat",
            language=lang,
            timestamp=datetime.now(timezone.utc),
            session_id=session_id,
        )
        # token = update_jwt(user_id, str(new_thread.id), session_id)

        await new_thread.save()

        return {"message": "Thread created successfully", "thread": new_thread}
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


@router.get("/select_threads")
async def select_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing or invalid")
        try:
            thread_obj_id = ObjectId(thread_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid thread ID format",
            )

        thread = await Thread.find_one(Thread.id == thread_obj_id)
        if not thread or thread.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this thread",
            )

        token = update_jwt(user_id, thread_id, session_id)

        return {"msg": token}
    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while selecting thread",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while selecting thread",
        )


@router.post("/change_language")
async def change_language(
    request: ChangeLangRequest, current_user: dict = Depends(get_current_user)
):
    try:
        try:
            thread_obj_id = ObjectId(request.thread_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid thread ID format",
            )

        thread = await Thread.find_one(Thread.id == thread_obj_id)
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this thread",
            )

        thread.language = request.language
        await thread.save()
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)

        return {"msg": "Language Changed SuccessFully"}
    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while selecting thread",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while selecting thread",
        )
