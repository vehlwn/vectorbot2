import telebot
import traceback

from async_bot import bot
from logger import logger, create_who_triggered_str


async def handle(message: telebot.types.Message):
    try:
        logger.info(f"[handle] /ping: {create_who_triggered_str(message)}")
        await bot.reply_to(message, "I'm alive!")
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
