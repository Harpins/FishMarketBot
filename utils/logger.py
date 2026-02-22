import logging
from telegram_handler import TelegramLoggingHandler   
from config import ERROR_BOT_TOKEN, ERROR_CHAT_ID

def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    try:
        tg_handler = TelegramLoggingHandler(
            ERROR_BOT_TOKEN, 
            ERROR_CHAT_ID,
            level=logging.ERROR,          
        )
        tg_handler.setFormatter(formatter) 
        logger.addHandler(tg_handler)
    except Exception as e:
        logger.error(f"Не удалось подключить Telegram handler: {e}")
    
    return logger