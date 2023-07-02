from sqlalchemy import select
import telebot
import typing
import traceback

from async_bot import bot
from logger import logger
from models import Currency, Point, User
import database
import strings


def _get_credits_string(chat_id: int, user_id: int) -> str:
    currencies: typing.Dict[str, int] = dict()
    with database.Session.begin() as session:
        result = session.execute(
            select(Point.value, Currency.name)
            .join(User.points)
            .join(Point.currency)
            .where((User.chat_id == chat_id) & (User.user_id == user_id))
        )
        for row in result:
            currencies[row.name] = row.value
    return "\n".join(
        [
            f"{value} {key}{strings.get_points_message_for_points(value)}"
            for key, value in currencies.items()
        ]
    )


async def _my_credits_command(message: telebot.types.Message):
    credits = _get_credits_string(message.chat.id, message.from_user.id)
    if len(credits) == 0:
        text = "У тебя нет баллов."
    else:
        text = f"У тебя:\n{credits}"
    await bot.reply_to(message, text)


async def handle(message: telebot.types.Message):
    try:
        logger.info(
            f"[handle] credits: {message.from_user.id} {message.from_user.first_name}"
        )
        if message.reply_to_message is None:
            await _my_credits_command(message)
            return
        user = message.reply_to_message.from_user
        credits = _get_credits_string(message.chat.id, user.id)
        if len(credits) == 0:
            text = "У {user.first_name} нет баллов."
        else:
            text = f"У {user.first_name}:\n{credits}"
        await bot.reply_to(message, text)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
