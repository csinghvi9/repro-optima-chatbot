from fastapi import HTTPException
from pymongo.errors import PyMongoError
from app.models.threads import Thread
from app.models.message import Message
from bson import ObjectId
from beanie import PydanticObjectId


async def get_thread_by_name(thread_id: str):
    try:
        thread_obj_id = ObjectId(thread_id)
    except Exception as e:
        return None

    thread = await Thread.find_one(Thread.id == thread_obj_id)

    if thread:
        return thread.thread_name

    return None


async def update_thread_name(thread_id: str, name: str) -> bool:
    try:
        # Validate ObjectId
        try:
            thread_obj_id = ObjectId(thread_id)
        except Exception as e:
            raise HTTPException(status_code=422, detail="Invalid thread ID format")
        thread = await Thread.find_one(Thread.id == thread_obj_id)

        if thread:
            thread.thread_name = name
            await thread.save()
            return True

        return False
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error while updating thread name"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error while updating thread name"
        )


async def delete_thread(thread_id: str):
    try:
        # Validate ObjectId
        try:
            object_id = PydanticObjectId(thread_id)
        except Exception as e:
            raise HTTPException(status_code=422, detail="Invalid thread ID format")
        thread = await Thread.get(object_id)

        if thread:
            await Message.find(Message.thread_id == thread_id).delete()
            await thread.delete()

            return {"message": "Thread and its messages deleted successfully"}

        return {"message": "Thread not found"}
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error during thread deletion"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error while deleting thread"
        )


async def update_thread_name_later(manager, thread_id, messages):
    chat_name = await manager.get_thread_name(messages)
    await update_thread_name(thread_id, chat_name)


def convert_objectid_to_str(obj):
    if isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    if isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj
