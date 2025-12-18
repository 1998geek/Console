from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Console Backend"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "YOUR_SUPER_SECRET_KEY_CHANGE_IT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Use DATABASE_URL from environment if available, otherwise default to a local testing one
    # Note: docker-compose sets DATABASE_URL=postgresql://postgres:postgres@db/ai_console
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/ai_console"
    )

    # =======================================================
    # Azure Cloud Services
    # =======================================================
    # OpenAI / LLM
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_TOKEN: str = os.getenv("AZURE_OPENAI_TOKEN", "")
    AZURE_GROK3_REST_ENDPOINT: str = os.getenv("AZURE_GROK3_REST_ENDPOINT", "")

    # Document Translation
    AZURE_DOCUMENT_TRANSLATION_ENDPOINT: str = os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT", "")
    AZURE_DOCUMENT_TRANSLATION_KEY: str = os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY", "")

    # Storage
    AZURE_STORAGE_ENDPOINT: str = os.getenv("AZURE_STORAGE_ENDPOINT", "")
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_KEY: str = os.getenv("AZURE_STORAGE_KEY", "")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "")
    AZURE_TARGET_CONTAINER_NAME: str = os.getenv("AZURE_TARGET_CONTAINER_NAME", "")
    AZURE_CONNECTION_STRING: str = os.getenv("AZURE_CONNECTION_STRING", "")

    class Config:
        case_sensitive = True

settings = Settings()
