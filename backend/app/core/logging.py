"""
Logging Configuration for LiveMind
Professional logging setup for development and production
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pythonjsonlogger import jsonlogger

from .config import settings

def setup_logging():
    """Setup comprehensive logging for LiveMind"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler for development
    if settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
    
    # File handler for all environments
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Configure specific loggers
    
    # LiveMind application logs
    livemind_logger = logging.getLogger("livemind")
    livemind_logger.setLevel(logging.INFO)
    
    # Pathway logs
    pathway_logger = logging.getLogger("pathway")
    pathway_logger.setLevel(getattr(logging, settings.PATHWAY_MONITORING_LEVEL.upper()))
    
    # FastAPI logs
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # Uvicorn logs
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # Suppress noisy third-party logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(f"🧠 LiveMind logging initialized - Level: {settings.LOG_LEVEL}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"livemind.{name}")
