import logging
import telebot

from settings import settings


def _find_numeric_level(s: str) -> int:
    ret = getattr(logging, s.upper(), None)
    if not isinstance(ret, int):
        raise ValueError(f"Invalid log level: {s}")
    return ret


def setup_logger():
    logger = logging.getLogger("vectorbot2")
    logging.basicConfig(format=settings.LOGGER_FORMAT)

    num_level = _find_numeric_level(settings.APP_LOG_LEVEL)
    logger.setLevel(num_level)

    num_level = _find_numeric_level(settings.TELEBOT_LOG_LEVEL)
    telebot.logger.setLevel(num_level)

    num_level = _find_numeric_level(settings.SQLALCHEMY_ENGINE_LOG_LEVEL)
    logging.getLogger("sqlalchemy.engine").setLevel(num_level)

    return logger


logger = setup_logger()
