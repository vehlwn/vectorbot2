from async_bot import bot
from . import ping, get_my_id, credits, rank, balls, change_credit
import settings


_CHAT_TYPES = ["private", "group"]


def register_all():
    bot.register_message_handler(
        ping.handle, commands=["ping"], chat_types=_CHAT_TYPES
    )
    bot.register_message_handler(
        get_my_id.handle, commands=["get_my_id"], chat_types=_CHAT_TYPES
    )
    bot.register_message_handler(
        credits.handle, commands=["credits"], chat_types=_CHAT_TYPES
    )
    bot.register_message_handler(
        rank.handle, commands=["rank"], chat_types=_CHAT_TYPES
    )
    bot.register_message_handler(
        balls.handle, commands=["balls"], chat_types=_CHAT_TYPES
    )
    bot.register_message_handler(
        change_credit.handle,
        regexp=settings.CHANGE_CREDIT_PATTERN,
        chat_types=_CHAT_TYPES,
    )
