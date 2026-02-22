"""Configuration management for Mark-X Enhanced."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_model: str = "arcee-ai/trinity-large-preview:free"
    
    # Voice Configuration
    vosk_model_path: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    
    # Wake Word Configuration
    porcupine_access_key: Optional[str] = None
    wake_word_enabled: bool = True
    
    # Telegram Bot
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Discord Bot
    discord_bot_token: Optional[str] = None
    discord_guild_id: Optional[str] = None
    
    # WhatsApp Configuration
    whatsapp_enabled: bool = False
    
    # Web API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change_this_secret_key"
    
    # Database
    database_path: str = "data/jarvis.db"
    
    # Memory Configuration
    vector_store_path: str = "data/vector_store"
    memory_retention_days: int = 90
    
    # Task Scheduler
    scheduler_enabled: bool = True
    
    # Webhook Server
    webhook_port: int = 8001
    webhook_secret: str = "your_webhook_secret"
    
    # General Settings
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_database_url(self) -> str:
        """Get full database URL."""
        db_path = BASE_DIR / self.database_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"
    
    def get_vector_store_path(self) -> Path:
        """Get full vector store path."""
        path = BASE_DIR / self.vector_store_path
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
