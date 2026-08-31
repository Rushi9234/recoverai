from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RecoverAI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./recoverai.db"
    
    # Application Environment
    ENVIRONMENT: str = "TEST"
    
    # Razorpay Integration Credentials
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None
    RAZORPAY_MODE: str = "test"
    RAZORPAY_WEBHOOK_SECRET: str = "whsec_test_secret_12345"
    
    # AI Provider Settings
    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "auto"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
