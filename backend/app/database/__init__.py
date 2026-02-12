# from beanie import init_beanie
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.utils.config import ENV_PROJECT
# from app.models.users import User
# from app.models.threads import Thread
# from app.models.message import Message
# from app.models.user_info import User_Info
# from app.models.ivf_centers import IVF_Center
# from app.models.otp_verification import OtpVerification
# from app.models.loan_model import Loan_User
# ivf_centers = None

# async def init_db():
#     try:
#         print("DataBase URL",ENV_PROJECT.DATABASE_URL)
#         client = AsyncIOMotorClient(ENV_PROJECT.DATABASE_URL)
#         database = client.get_database("indra_ivf")
#         # Initialize Beanie with the database and models
#         await init_beanie(database, document_models=[User, Thread,User_Info,IVF_Center,OtpVerification,Loan_User])
#     except Exception as e:
#         print(f"Error initializing database: {e}")
#         raise


from azure.identity import AzureCliCredential, DefaultAzureCredential, EnvironmentCredential
from azure.keyvault.secrets import SecretClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.utils.config import ENV_PROJECT


# Key Vault and DB config from .env
KEY_VAULT_URL = ENV_PROJECT.KEY_VAULT_URL
SECRET_NAME = ENV_PROJECT.SECRET_NAME
DATABASE_URL = ENV_PROJECT.DATABASE_URL
MONGO_DB_NAME = ENV_PROJECT.MONGO_DB_NAME 

# Models
from app.models.users import User
from app.models.threads import Thread
from app.models.message import Message
from app.models.user_info import User_Info
from app.models.ivf_centers import IVF_Center
from app.models.otp_verification import OtpVerification
from app.models.loan_model import Loan_User
from app.models.videos import Video

# Global DB client and instance
db_client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

async def init_db():
    global db_client, database

    try:
        # Azure Key Vault client (uses az login for local dev)
        # credential = AzureCliCredential()
        # credential = DefaultAzureCredential() 
        credential = EnvironmentCredential()
        print("✅ Azure CLI credential acquired.", DATABASE_URL)
        print("🔐 Connecting to Azure Key Vault...", KEY_VAULT_URL)
        secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

        # Fetch password and build full URI
        print(f"🔐 Fetching DB password for secret: {SECRET_NAME}...")
        db_password = secret_client.get_secret(SECRET_NAME).value
        print("✅ DB password fetched.", db_password)
        final_db_uri = DATABASE_URL.replace("{password}", db_password)

        print("🔐 Connecting to MongoDB...", final_db_uri)

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
                OtpVerification,
                Loan_User,
                Video
            ]
        )

        print(f"✅ MongoDB connected and Beanie initialized for database: {MONGO_DB_NAME}")
    except Exception as e:
        print(f"❌ Error initializing DB: {e}")
        raise
