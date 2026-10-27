import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    APP_NAME: str = "EventHorizon AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8001
    FRONTEND_PORT: int = 5173
    
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:5174", 
        "http://127.0.0.1:5174", 
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001"
    ]
    
    # Database
    # Default to SQLite for seamless zero-dependency local development and testing,
    # or PostgreSQL when configured via environment
    DATABASE_URL: str = "sqlite+aiosqlite:///./eventhorizon.db"
    
    # Redis / Workers
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Auth & Tokens
    SECRET_KEY: str = "eventhorizon-super-secure-production-ready-jwt-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ANONYMOUS_EVENT_VIEW_LIMIT: int = 5
    
    # AI Engine
    AI_PROVIDER: str = "gemini"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-2.5-flash"
    
    # Crawler & Fetcher
    CRAWLER_USER_AGENT: str = "EventHorizonBot/1.0 (+https://eventhorizon.ai/bot; verification-crawler)"
    CRAWLER_TIMEOUT_SECONDS: int = 15
    CRAWLER_MAX_CONTENT_BYTES: int = 5242880  # 5 MB max
    SSRF_PROTECTION_ENABLED: bool = True
    
    # Initial Admin Seed
    INITIAL_SUPERADMIN_EMAIL: str = "admin@eventhorizon.ai"
    INITIAL_SUPERADMIN_PASSWORD: str = "Admin@EventHorizon2026!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
