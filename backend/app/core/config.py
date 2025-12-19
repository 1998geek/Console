import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API 基础配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Portal Backend"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "unsafe-default-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))
    
    # 数据库配置
    DATABASE_HOST: str = os.getenv("DATABASE_HOST")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    DATABASE_USER: str = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")

    # Redis 配置
    REDIS_HOST: str = "redis"  # docker-compose service name
    REDIS_PORT: int = 6379

    # Azure Storage 配置
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "translatecontainer")
    AZURE_TARGET_CONTAINER_NAME: str = os.getenv("AZURE_TARGET_CONTAINER_NAME", "translatettcontainer")
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    AZURE_STORAGE_KEY: str = os.getenv("AZURE_STORAGE_KEY")
    AZURE_STORAGE_ENDPOINT: str = os.getenv("AZURE_STORAGE_ENDPOINT")

    # Azure Translation 配置
    AZURE_DOCUMENT_TRANSLATION_ENDPOINT: str = os.getenv("AZURE_DOCUMENT_TRANSLATION_ENDPOINT")
    AZURE_DOCUMENT_TRANSLATION_KEY: str = os.getenv("AZURE_DOCUMENT_TRANSLATION_KEY")

settings = Settings()
