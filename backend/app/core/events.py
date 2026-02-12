from beanie import init_beanie
from fastapi import FastAPI
from loguru import logger
from app.utils.config import ENV_PROJECT

# from app.database import mongodb
# from app.modules.async_redis_consumer import aredis, start_redis_consumer
import asyncio
from typing import Callable
from app.core.kbSetUP import KBSetup

# import certifi
from app.models.threads import Thread
from app.models.message import Message
from app.models.users import User
from app.models.user_info import User_Info
from app.models.otp_verification import OtpVerification
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import init_db

listen_task = None


def create_start_app_handler(app: FastAPI) -> Callable:

    @logger.catch
    async def start_app() -> None:
        try:

            # print("DataBase URL",ENV_PROJECT.DATABASE_URL)
            # client = AsyncIOMotorClient(ENV_PROJECT.DATABASE_URL) #,tlsCAFile=certifi.where())
            # database = client.get_database("indra_ivf")
            # # Initialize Beanie with the database and models
            # await init_beanie(database, document_models=[User, Thread, Message,User_Info,OtpVerification])
            # app.state.ivf_centers = database.get_collection("IVFCenters")

            await init_db()
            await KBSetup()
            logger.info("Knowledge Base Setup Completed.")

            # await start_redis()
            # logger.info("Redis Connected.")

        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise e

    return start_app


# def create_stop_app_handler(app: FastAPI) -> Callable:

#     @logger.catch
#     async def stop_app() -> None:
#         try:
#             mongodb.client.close()
#             logger.info("Closed MongoDB Connection")

#             # await stop_redis()
#             # logger.info("Closed Redis Connection")

#         except Exception as e:
#             logger.error(f"Shutdown error: {e}")
#             raise e

#     return stop_app


# async def start_redis():
#     global listen_task
#     try:
#         if await aredis.client.ping():
#             listen_task = asyncio.create_task(start_redis_consumer("run_chat"))
#     except Exception as e:
#         logger.error(f"Redis start error: {e}")
#         raise e


# async def stop_redis():
#     global listen_task
#     try:
#         await aredis.pubsub.close()
#         await aredis.close()
#         logger.info("Redis connection closed.")
#     except Exception as e:
#         logger.error(f"Redis stop error: {e}")
#         raise e
#     finally:
#         logger.info("Background PubSub Listener stopped.")
#         if listen_task:
#             listen_task.cancel()
