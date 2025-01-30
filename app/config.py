from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # API Keys and URLs
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DEEPSEEK_API_KEY: str
    PADDLE_PUBLIC_KEY: str
    PADDLE_VENDOR_ID: str

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # JWT Settings
    JWT_SECRET: str = "your_jwt_secret_key"
    JWT_ALGORITHM: str = "HS256"

    # API Settings
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Application Settings
    INITIAL_FREE_CREDITS: int = 10

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