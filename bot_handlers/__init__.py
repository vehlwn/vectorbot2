import telebot

from . import start, help, ping, get_my_id, credits, rank, balls, change_credit
from async_bot import bot
from logger import logger
import settings


_CHAT_TYPES = ["private", "group", "supergroup"]


async def register_all():
    bot.register_message_handler(
        start.handle,
        commands=["start"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        help.handle,
        commands=["help"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        ping.handle,
        commands=["ping"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        get_my_id.handle,
        commands=["get_my_id"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        credits.handle,
        commands=["credits"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        rank.handle,
        commands=["rank"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        balls.handle,
        commands=["balls", "шары"],
        chat_types=_CHAT_TYPES,
        match_bot_username=True,
    )
    bot.register_message_handler(
        change_credit.handle,
        regexp=settings.CHANGE_CREDIT_PATTERN,
        chat_types=_CHAT_TYPES,
    )
    await _register_commands()


async def _register_commands():
    my_commands = [
        telebot.types.BotCommand(cmd, desc) for cmd, desc in help.AVAILABLE_COMMANDS
    ]
    if not await bot.set_my_commands(my_commands):
        logger.error("Failed to register commands list")
