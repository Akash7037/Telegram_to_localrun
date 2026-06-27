import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    WHITELISTED_CHAT_ID = int(os.getenv("WHITELISTED_CHAT_ID", 0))
    
    # Power management settings
    POWER_CHECK_INTERVAL = int(os.getenv("POWER_CHECK_INTERVAL", 30))  # seconds
    IDLE_POWER_CHECK_INTERVAL = int(os.getenv("IDLE_POWER_CHECK_INTERVAL", 60))  # seconds
    
    # Telegram polling settings
    POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", 25))  # seconds
    
    # LLM settings
    PRIMARY_LLM_PROVIDER = os.getenv("PRIMARY_LLM_PROVIDER", "google")  # "google", "openai", "anthropic", "openrouter"
    PRIMARY_LLM_API_KEY = os.getenv("PRIMARY_LLM_API_KEY")
    PRIMARY_LLM_MODEL = os.getenv("PRIMARY_LLM_MODEL", "gemini-pro")

    FALLBACK_LLM_PROVIDER = os.getenv("FALLBACK_LLM_PROVIDER", "openrouter") # "google", "openai", "anthropic", "openrouter"
    FALLBACK_LLM_API_KEY = os.getenv("FALLBACK_LLM_API_KEY")
    FALLBACK_LLM_MODEL = os.getenv("FALLBACK_LLM_MODEL", "google/gemini-pro") # Example for OpenRouter
    
    # Logging settings
    LOG_FILE = os.getenv("LOG_FILE", "assistant.log")
    MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 5 * 1024 * 1024))  # 5MB
    BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 3))

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.WHITELISTED_CHAT_ID:
            missing.append("WHITELISTED_CHAT_ID")
        
        if not cls.PRIMARY_LLM_API_KEY:
            missing.append("PRIMARY_LLM_API_KEY")
        
        # Fallback LLM is optional, but if provider is set, key should be too
        if cls.FALLBACK_LLM_PROVIDER and not cls.FALLBACK_LLM_API_KEY:
            missing.append("FALLBACK_LLM_API_KEY")

        if missing:
            raise ValueError(f"Missing required configuration: {", ".join(missing)}")
