from fastapi import HTTPException
from app.models.users import User
from beanie.exceptions import DocumentNotFound
from passlib.context import CryptContext
from typing import Optional
from bson import ObjectId
import logging
from pymongo.errors import PyMongoError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


async def hash_password(password: str) -> str:
    try:
        if not isinstance(password, str) or not password.strip():
            raise HTTPException(status_code=422, detail="Invalid password input")

        return pwd_context.hash(password)

    except ValueError as ve:
        logger.error(f"ValueError in hashing password: {ve}")
        raise HTTPException(status_code=400, detail="Password value error")

    except Exception as e:
        logger.exception(f"Unexpected error during password hashing: {e}")
        raise HTTPException(status_code=500, detail="Failed to securely hash password")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not plain_password or not hashed_password:
            raise HTTPException(
                status_code=422, detail="Password fields cannot be empty"
            )

        return pwd_context.verify(plain_password, hashed_password)

    except ValueError as ve:
        logger.error(f"ValueError in password verification: {ve}")
        raise HTTPException(status_code=400, detail="Password verification failed")

    except Exception as e:
        logger.exception(f"Unexpected error during password verification: {e}")
        raise HTTPException(
            status_code=500, detail="Internal error during password check"
        )


async def create_user(user_data, role) -> User:
    try:
        # Validate essential fields
        if not user_data.name or not user_data.email or not user_data.password:
            raise HTTPException(status_code=422, detail="Missing required fields")

        password_hash = await hash_password(user_data.password)

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            role_name=role,
        )

        await user.insert()
        return user

    except PyMongoError as db_exc:
        logger.error(f"Database error while creating user: {db_exc}")
        raise HTTPException(
            status_code=500, detail="Database error during user creation"
        )

    except HTTPException as http_exc:
        raise http_exc  # re-raise FastAPI's HTTPException cleanly

    except Exception as e:
        logger.exception(f"Unexpected error in create_user: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred during user creation"
        )


async def update_password(user_id: str, password: str):
    try:
        user = await get_user_by_id(user_id)
        if user:
            password_hash = await hash_password(password)
            user.password_hash = password_hash
            await user.save()
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_user_by_email(email: str) -> Optional[User]:
    try:
        user = await User.find_one(User.email == email)
        return user
    except DocumentNotFound:
        logger.warning(f"User not found with email: {email}")
        return None
    except PyMongoError as e:
        logger.error(f"Database error while retrieving user by email: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_user_by_email: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        user_obj_id = ObjectId(user_id)
        user = await User.find_one(User.id == user_obj_id)
        return user
    except DocumentNotFound:
        return None


async def verify_user_password(user: User, password: str) -> bool:
    try:
        if not user or not isinstance(user.password_hash, str):
            raise HTTPException(status_code=400, detail="Invalid user data")

        if not isinstance(password, str) or not password.strip():
            raise HTTPException(status_code=422, detail="Invalid password input")

        return await verify_password(password, user.password_hash)

    except ValueError as ve:
        logger.error(f"ValueError during password verification: {ve}")
        raise HTTPException(status_code=400, detail="Password verification error")

    except Exception as e:
        logger.exception(f"Unexpected error in verify_user_password: {e}")
        raise HTTPException(
            status_code=500, detail="Internal error during password verification"
        )


# async def create_message(
#     content: Union[str, List[str]],
#     sender: str,
#     thread_id: str,
# ) -> Message:
#     message = Message(
#         content=content,
#         role=sender,
#         sender=sender,
#         thread_id=thread_id,
#         timestamp=datetime.utcnow(),
#         feedback=-1,
#     )

#     await message.insert()
#     return message


# async def get_all_messages(thread_id: str) -> List:
#     message_objs = (
#         await Message.find(Message.thread_id == thread_id)
#         .sort(Message.timestamp)
#         .to_list()
#     )

#     formatted_messages = [
#         {"role": msg.sender, "content": msg.content} for msg in message_objs
#     ]

#     return formatted_messages


# async def get_thread_by_name(thread_id: str):
#     try:
#         thread_obj_id = ObjectId(thread_id)
#     except Exception as e:
#         print(f"Invalid ObjectId: {e}")
#         return None

#     thread = await Thread.find_one(Thread.id == thread_obj_id)

#     if thread:
#         print("thread_found")
#         return thread.thread_name

#     return None


# async def update_thread_name(thread_id: str, name: str) -> bool:
#     try:
#         thread_obj_id = ObjectId(thread_id)
#         thread = await Thread.find_one(Thread.id == thread_obj_id)

#         if thread:
#             thread.thread_name = name
#             await thread.save()
#             return True

#         return False
#     except Exception as e:
#         print(f"Error updating thread name: {e}")
#         return False


# async def get_user_last_message(thread_id):
#     message = (
#         await Message.find(Message.thread_id == thread_id, Message.sender == "user")
#         .sort("-timestamp")
#         .first_or_none()
#     )

#     if message is None:
#         return "No message yet"

#     return message.content

# async def delete_thread(thread_id: str):
#     thread = await Thread.get(PydanticObjectId(thread_id))

#     if thread:
#         await Message.find(Message.thread_id == thread_id).delete()
#         await thread.delete()

#         return {"message": "Thread and its messages deleted successfully"}

#     return {"message": "Thread not found"}


# async def update_thread_name_later(manager, thread_id, messages):
#     chat_name = await manager.get_thread_name(messages)
#     await update_thread_name(thread_id, chat_name)
