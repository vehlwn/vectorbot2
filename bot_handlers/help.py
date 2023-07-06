import telebot
import traceback

from async_bot import bot
from logger import logger, create_who_triggered_str


AVAILABLE_COMMANDS = [
    ("start", "Start the bot"),
    ("help", "Display this help message"),
    ("ping", "Tests if bot's alive"),
    ("get_my_id", "Returns your user_id"),
    ("credits", "Shows your or other user's points balance"),
    ("rank", "<currency_name> Shows users with the most currency_name points"),
    ("balls", "Sort all currencies by the amount of users"),
]


async def handle(message: telebot.types.Message):
    try:
        logger.info(f"[handle] /help: {create_who_triggered_str(message)}")
        text = "Available commands:\n\n"
        for command, description in AVAILABLE_COMMANDS:
            text += f"- {command} - {description}\n"
        await bot.reply_to(message, text)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
