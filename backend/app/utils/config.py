from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required — core app functionality
    GUEST_TOKEN_SECRET_KEY: str
    ADMIN_SECRET_KEY: str
    ADMIN_REFRESH_SECRET_KEY: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str

    GUEST_TOKEN_EXPIRY_SECONDS: int = 604800
    GUEST_TOKEN_EXPIRY_DAYS: int = 7
    REFRESH_TOKEN_EXPIRY_DAYS: int = 30

    DATABASE_URL: str
    PORT: int = 10000
    MONGO_DB_NAME: str = "IVF_CHATBOT"

    # Azure Key Vault — optional (not needed for free deployment)
    KEY_VAULT_URL: str = ""
    SECRET_NAME: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_TENANT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""

    # SSH tunnel — optional
    USE_SSH_TUNNEL: bool = False
    SSH_USER: str = ""
    SSH_HOST: str = ""
    SSH_PORT: str = ""
    SSH_KEY_PATH: str = ""

    # MongoDB connection details — optional (not needed when using Atlas connection string)
    MONGO_CA_FILE: str = ""
    MONGO_SECRET_NAME: str = ""
    MONGO_PORT: int = 27017
    MONGO_HOST: str = ""

    # AWS — optional (not needed if not using S3 videos)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    REPO_NAME: str = ""

    # TLS — optional
    MONGO_TLS_CA_FILE: str = ""
    MONGO_TLS_CERT_FILE: str = ""
    MONGO_TLS_ALLOW_INVALID_HOSTNAMES: bool = True

    # Email — optional
    ADMIN_EMAIL_ID: str = ""
    ADMIN_EMAIL_TO: str = ""
    MAIL_PASSWORD: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


ENV_PROJECT = Settings()
