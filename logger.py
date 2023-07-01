import logging
import telebot

import settings

def setup_logger():
    logger = logging.getLogger("vectorbot2")
    logging.basicConfig(format=settings.LOGGER_FORMAT)
    log_level = settings.LOG_LEVEL.upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logger.setLevel(numeric_level)
    telebot.logger.setLevel(numeric_level)
    return logger


logger = setup_logger()
