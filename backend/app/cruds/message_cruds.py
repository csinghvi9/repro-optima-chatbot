from fastapi import HTTPException
from app.models.message import Message
from typing import Union, List
from datetime import datetime, timezone
from pymongo.errors import PyMongoError


async def create_message(
    content: Union[str, List[str]],
    sender: str,
) -> Message:
    try:
        # Input validation
        if not content or not sender:
            raise HTTPException(
                status_code=422, detail="Missing required message fields"
            )

        if not isinstance(content, (str, list)):
            raise HTTPException(
                status_code=422, detail="Content must be a string or list of strings"
            )

        if isinstance(content, list) and not all(
            isinstance(item, str) for item in content
        ):
            raise HTTPException(
                status_code=422, detail="All list items in content must be strings"
            )
        message = Message(
            content=content,
            role=sender,
            sender=sender,
            timestamp=datetime.now(timezone.utc),
            feedback=-1,
        )

        await message.insert()
        return message
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error while creating message"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while creating message"
        )


async def get_all_messages(thread_id: str) -> List:
    try:
        # Validate input
        if not thread_id or not isinstance(thread_id, str):
            raise HTTPException(status_code=422, detail="Invalid thread ID")
        message_objs = (
            await Message.find(Message.thread_id == thread_id)
            .sort(Message.timestamp)
            .to_list()
        )

        formatted_messages = [
            {"role": msg.sender, "content": msg.content} for msg in message_objs
        ]

        return formatted_messages
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error while fetching messages"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching messages"
        )


async def get_user_last_message(thread_id):
    message = (
        await Message.find(Message.thread_id == thread_id, Message.sender == "user")
        .sort("-timestamp")
        .first_or_none()
    )

    if message is None:
        return "No message yet"

    return message.content
