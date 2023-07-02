from sqlalchemy import select, desc, func
import telebot

from async_bot import bot
from models import Currency, Point, User
import database
import settings
import strings


async def handle(message: telebot.types.Message):
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
