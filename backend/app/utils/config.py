from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GUEST_TOKEN_SECRET_KEY: str
    ADMIN_SECRET_KEY: str
    ADMIN_REFRESH_SECRET_KEY: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str

    GUEST_TOKEN_EXPIRY_SECONDS: int
    GUEST_TOKEN_EXPIRY_DAYS: int
    REFRESH_TOKEN_EXPIRY_DAYS: int

    DATABASE_URL: str
    PORT: int
    KEY_VAULT_URL: str
    SECRET_NAME: str
    AZURE_CLIENT_ID: str
    AZURE_TENANT_ID: str
    AZURE_CLIENT_SECRET: str

    USE_SSH_TUNNEL: bool
    SSH_USER: str
    SSH_HOST: str
    SSH_PORT: str
    SSH_KEY_PATH: str
    MONGO_CA_FILE: str
    MONGO_SECRET_NAME: str
    MONGO_DB_NAME: str
    MONGO_PORT: int
    MONGO_HOST: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    REPO_NAME: str

    # New fields for TLS
    MONGO_TLS_CA_FILE: str  # Path to the CA certificate file
    MONGO_TLS_CERT_FILE: str  # Path to the client certificate file (optional)
    MONGO_TLS_ALLOW_INVALID_HOSTNAMES: bool = True

    S3_VIDEO_BUCKET: str
    DOCTOR_TESTIMONIAL_VIDEOKEY: list
    PATIENT_TESTIMONIAL_VIDEOKEY: list
    PATIENT_TESTIMONIAL_THUMBNAIL: list
    DOCTOR_TESTIMONIAL_THUMBNAIL: list
    SUCCESS_RATE_VIDEOKEY: list
    SUCCESS_RATE_THUMBNAIL: list
    ADMIN_EMAIL_ID: str
    ADMIN_EMAIL_TO: str
    MAIL_PASSWORD: str
    IVF_COST_VIDEOKEY: list
    IVF_COST_THUMBNAIL: list
    DOCTOR_HEADING: list
    PATIENT_HEADING: list
    SUCCESS_HEADING: list
    COST_HEADING: list
    IVF_INFORMATION_HEADING: list
    IVF_INFORMATION_THUMBNAIL: list
    IVF_INFORMATION_VIDEOKEY: list
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


ENV_PROJECT = Settings()
