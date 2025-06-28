"""
Core Configuration Settings for LiveMind
Using FREE services to keep costs at $0!
"""

import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import validator

class Settings(BaseSettings):
    # =============================================================================
    # 🚀 APPLICATION SETTINGS
    # =============================================================================
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "livemind-secret-change-in-production"
    
    # =============================================================================
    # 🔑 FREE LLM API SETTINGS (No costs!)
    # =============================================================================
    # Groq API (FREE and FAST!)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-8b-8192"  # Free and lightning fast!
    
    # Backup free options
    HUGGINGFACE_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""
    
    # =============================================================================
    # 📊 FREE DATA SOURCE APIs
    # =============================================================================
    # News (Free tiers)
    NEWS_API_KEY: str = ""  # 1000 requests/day free
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    
    # Financial (Free)
    ALPHA_VANTAGE_API_KEY: str = ""  # 5 requests/minute free
    
    # Weather (Free)
    OPENWEATHER_API_KEY: str = ""  # 1000 calls/day free
    
    # =============================================================================
    # 🗄️ DATABASE SETTINGS (Using free local storage)
    # =============================================================================
    VECTOR_DB_TYPE: str = "chroma"  # Free local vector DB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # Redis for caching (can use local Redis)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    
    # =============================================================================
    # 🔄 PATHWAY SETTINGS
    # =============================================================================
    PATHWAY_CACHE_DIR: str = "./data/pathway_cache"
    PATHWAY_MONITORING_LEVEL: str = "INFO"
    
    # =============================================================================
    # 🌐 CORS SETTINGS
    # =============================================================================
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # =============================================================================
    # 📝 LOGGING
    # =============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/livemind.log"
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs(settings.PATHWAY_CACHE_DIR, exist_ok=True)
