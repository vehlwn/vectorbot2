from sqlalchemy import select, desc, func
import telebot
import traceback

from async_bot import bot
from logger import logger
from models import Currency, Point, User
from settings import settings
import database
import strings


async def _handle_impl(message: telebot.types.Message):
    count = settings.MAX_BALLS_ROWS
    chat_id = message.chat.id
    with database.Session.begin() as session:
        result = session.execute(
            select(Currency.name, func.count(User.user_id).label("count"))
            .join(User.points)
            .join(Point.currency)
            .where(User.chat_id == chat_id)
            .group_by(Currency.id)
            .order_by(desc("count"))
            .limit(count)
        )
        text = ""
        for row in result:
            text += "{}баллы ➔ {} {}\n".format(
                row.name,
                row.count,
                strings.get_holders_message_for_holders(row.count),
            )
    await bot.reply_to(message, text)


async def handle(message: telebot.types.Message):
    try:
        logger.info(
            f"[handle] balls: {message.from_user.id} {message.from_user.first_name}"
        )
        await _handle_impl(message)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
