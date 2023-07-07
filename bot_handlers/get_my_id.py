import telebot
import traceback

from async_bot import bot
from logger import logger, create_who_triggered_str


async def handle(message: telebot.types.Message):
    try:
        logger.info(f"[handle] /get_my_id: {create_who_triggered_str(message)}")
        text = f"chat_id = {message.chat.id}\n"
        text += f"user_id = {message.from_user.id}"
        await bot.reply_to(message, text)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
