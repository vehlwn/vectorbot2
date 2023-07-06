from sqlalchemy import select, desc
import telebot
import traceback
import typing

from async_bot import bot
from logger import logger, create_who_triggered_str
from models import Currency, Point, User
import database
import strings


async def _get_first_name(user_id: int):
    chat = await bot.get_chat(user_id)
    return chat.first_name


async def _handle_impl(message: telebot.types.Message):
    argument = telebot.util.extract_arguments(typing.cast(str, message.text))
    if len(argument) == 0:
        currency = strings.CREDIT_BOT_DEFAULT_CURRENCY
    else:
        currency = argument

    chat_id = message.chat.id
    with database.Session.begin() as session:
        result = session.execute(
            select(User.user_id, Point.value)
            .join(User.points)
            .join(Point.currency)
            .where((User.chat_id == chat_id) & (Currency.name == currency))
            .order_by(desc(Point.value))
        )
        leaderboard = []
        for row in result:
            leaderboard.append((row.user_id, row.value))

    best = leaderboard[:3]
    worst = leaderboard[3:][-3:]
    text = f"Больше всего {currency}баллов:\n"
    if len(best) == 0:
        text += "ни у кого!"

    async def concat_values(leaderboard):
        ret = ""
        for user_id, value in leaderboard:
            ret += "{} ➔ {}\n".format(await _get_first_name(user_id), str(value))
        return ret

    text += await concat_values(best)
    text += await concat_values(worst)
    await bot.reply_to(message, text)


async def handle(message: telebot.types.Message):
    try:
        logger.info(
            f"[handle] /rank: {create_who_triggered_str(message)} text={message.text}"
        )
        await _handle_impl(message)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
