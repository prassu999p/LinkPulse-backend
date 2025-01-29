from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str
    
    # Paddle Configuration
    PADDLE_PUBLIC_KEY: str
    PADDLE_VENDOR_ID: str
    
    # Application Configuration
    INITIAL_FREE_CREDITS: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 