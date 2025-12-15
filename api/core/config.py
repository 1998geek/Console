"""
Configuration Management
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "AIPortal API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-use-strong-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # In production, specify allowed origins
    
    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: Optional[str] = None
    DATABASE_PORT: Optional[str] = None
    DATABASE_NAME: Optional[str] = None
    DATABASE_USER: Optional[str] = None
    DATABASE_PASSWORD: Optional[str] = None
    
    # Azure Services
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_ENDPOINT: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_KEY: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME: Optional[str] = None
    AZURE_TARGET_CONTAINER_NAME: Optional[str] = None
    AZURE_CONNECTION_STRING: Optional[str] = None
    
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_KEY: Optional[str] = None
    
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_TOKEN: Optional[str] = None
    AZURE_GROK3_REST_ENDPOINT: Optional[str] = None
    
    AZURE_DOCUMENT_TRANSLATION_ENDPOINT: Optional[str] = None
    AZURE_DOCUMENT_TRANSLATION_KEY: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # XInference
    XINFERENCE_BASE_URL: Optional[str] = None
    XINFERENCE_TRANSLATE_MODEL_NAME: Optional[str] = None
    
    # Aliyun AI
    ALIYUN_AI_ENDPOINT: Optional[str] = None
    ALIYUN_AI_TOKEN: Optional[str] = None
    
    # Dify
    DIFY_API_BASE_URL_DEFAULT: Optional[str] = None
    DIFY_API_KEY_DEFAULT: Optional[str] = None
    DIFY_API_CASE_STUDY_URL: Optional[str] = None
    DIFY_API_CASE_STUDY_KEY: Optional[str] = None
    
    # Email/SMTP
    SENDER_USERNAME: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[str] = None
    TO_ADDRS: Optional[str] = None
    FROM_ALIAS: Optional[str] = None
    
    # RSS
    RSS_URL: Optional[str] = None
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "/tmp/uploads"
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".pptx", ".xlsx", ".txt"}
    
    # Task Queue
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Pydantic V2 configuration
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env file
    )


# Global settings instance
settings = Settings()
