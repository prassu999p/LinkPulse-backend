from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # API Keys and URLs
    SUPABASE_URL: str
    SUPABASE_KEY: str  # anon key for client operations
    SUPABASE_SERVICE_KEY: str  # service_role key for admin operations
    DEEPSEEK_API_KEY: str
    PADDLE_PUBLIC_KEY: str
    PADDLE_VENDOR_ID: str

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # JWT Settings
    JWT_SECRET: str = "your_jwt_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Settings
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Application Settings
    INITIAL_FREE_CREDITS: int = 50
    PRO_PLAN_CREDITS: int = 500

    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    ADMIN_EMAIL: str

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 