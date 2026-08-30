import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "A Job in AI Era"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))

    # OpenRouter API
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # AI Models (Using valid OpenRouter slugs)
    MODEL_CHAT: str = os.getenv("MODEL_CHAT", "qwen/qwen-2.5-72b-instruct")
    MODEL_PARSING: str = os.getenv("MODEL_PARSING", "qwen/qwen-2.5-72b-instruct")
    MODEL_MATCHING: str = os.getenv("MODEL_MATCHING", "deepseek/deepseek-chat")
    MODEL_COVER_LETTER: str = os.getenv("MODEL_COVER_LETTER", "deepseek/deepseek-chat")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/antigravity_db")

    # Qdrant Vector Store
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
