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
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "anthropic"
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini" if LLM_PROVIDER == "openai" else "claude-3-haiku-20240307")
    
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
        if not cls.LLM_API_KEY:
            missing.append("LLM_API_KEY")
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
