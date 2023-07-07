import telebot
import traceback

from async_bot import bot
from logger import logger, create_who_triggered_str


def _get_id_string(chat_id: int, user_id: int):
    text = f"chat_id = {chat_id}\n"
    text += f"user_id = {user_id}"
    return text


async def handle(message: telebot.types.Message):
    try:
        logger.info(f"[handle] /get_my_id: {create_who_triggered_str(message)}")
        if message.reply_to_message is None:
            text = "Твой id:\n"
            text += _get_id_string(message.chat.id, message.from_user.id)
        else:
            r = message.reply_to_message
            text = f"{r.from_user.first_name} id:\n"
            text += _get_id_string(r.chat.id, r.from_user.id)
        await bot.reply_to(message, text)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
