from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.utils.config import ENV_PROJECT

DATABASE_URL = ENV_PROJECT.DATABASE_URL
MONGO_DB_NAME = ENV_PROJECT.MONGO_DB_NAME

# Models
from app.models.users import User
from app.models.threads import Thread
from app.models.message import Message
from app.models.user_info import User_Info
from app.models.ivf_centers import IVF_Center
from app.models.otp_verification import OtpVerification

# Global DB client and instance
db_client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

async def init_db():
    global db_client, database

    try:
        use_keyvault = getattr(ENV_PROJECT, 'KEY_VAULT_URL', '') and getattr(ENV_PROJECT, 'AZURE_CLIENT_ID', '')

        if use_keyvault and ENV_PROJECT.KEY_VAULT_URL and "{password}" in DATABASE_URL:
            # Azure Key Vault mode: fetch password from Key Vault
            from azure.identity import EnvironmentCredential
            from azure.keyvault.secrets import SecretClient

            credential = EnvironmentCredential()
            secret_client = SecretClient(vault_url=ENV_PROJECT.KEY_VAULT_URL, credential=credential)
            db_password = secret_client.get_secret(ENV_PROJECT.SECRET_NAME).value
            final_db_uri = DATABASE_URL.replace("{password}", db_password)
            print(f"Connected using Azure Key Vault for database: {MONGO_DB_NAME}")
        else:
            # Direct connection mode: DATABASE_URL contains the full connection string
            final_db_uri = DATABASE_URL
            print(f"Connected using direct DATABASE_URL for database: {MONGO_DB_NAME}")

        # Connect to MongoDB
        db_client = AsyncIOMotorClient(final_db_uri)
        database = db_client.get_database(MONGO_DB_NAME)

        # Initialize Beanie ODM with all document models
        await init_beanie(
            database,
            document_models=[
                User,
                Thread,
                Message,
                User_Info,
                IVF_Center,
                OtpVerification
            ]
        )

        print(f"MongoDB connected and Beanie initialized for database: {MONGO_DB_NAME}")
    except Exception as e:
        print(f"Error initializing DB: {e}")
        raise
