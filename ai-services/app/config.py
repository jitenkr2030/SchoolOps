"""
Configuration settings for AI Services
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "SchoolOps AI Services"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Backend API
    BACKEND_API_URL: str = "http://localhost:8000"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # ML Models
    MODEL_CACHE_DIR: str = "./models"
    USE_GPU: bool = False

    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Hugging Face
    HF_TOKEN: str = ""
    HF_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LangChain
    LANGCHAIN_TRACING: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
