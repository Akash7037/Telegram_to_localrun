import logging
from logging.handlers import RotatingFileHandler
from .config import Config

def setup_logger():
    logger = logging.getLogger("LaptopAssistant")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = RotatingFileHandler(
            Config.LOG_FILE, 
            maxBytes=Config.MAX_LOG_SIZE, 
            backupCount=Config.BACKUP_COUNT
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Also log to console for development/initial setup (can be removed for pure background)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()
