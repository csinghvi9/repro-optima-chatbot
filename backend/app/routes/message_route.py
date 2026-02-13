from fastapi import APIRouter, HTTPException, Depends, status
from app.cruds.message_cruds import create_message, get_all_messages
from app.auth.auth import get_current_user
from pydantic import ValidationError
from app.schemas.message_schemas import MessageCreate
from pymongo.errors import PyMongoError


# class MessageCreate(BaseModel):
#     content: Union[str, List[str]]
#     sender: str


router = APIRouter()


@router.get("/get_all_messages/")
async def get_all_messages_route(current_user: dict = Depends(get_current_user)):
    try:
        thread_id = current_user["thread_id"]
        if not thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thread ID not found in token",
            )

        messages = await get_all_messages(thread_id)
        return {"messages": messages}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages",
        )


@router.post("/messages/")
async def post_message(
    msg: MessageCreate, current_user: dict = Depends(get_current_user)
):
    try:

        user_id = current_user["thread_id"]
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thread ID missing in token",
            )

        message = await create_message(
            content=msg.content, sender=msg.sender, thread_id=user_id
        )

        return {"message": "Message created successfully", "data": message}

    except ValidationError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid message data",
        )

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating message",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while posting message",
        )
