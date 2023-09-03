from sqlalchemy import select, desc
from telebot.asyncio_helper import ApiTelegramException
import sqlalchemy.orm
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


async def _create_leaderboard(
    session: sqlalchemy.orm.Session, chat_id: int, currency: str
):
    result = session.execute(
        select(User, Point.value)
        .join(User.points)
        .join(Point.currency)
        .where((User.chat_id == chat_id) & (Currency.name == currency))
        .order_by(desc(Point.value))
    )
    ret = []
    for row in result:
        try:
            first_name = await _get_first_name(row.User.user_id)
        except ApiTelegramException as er:
            if "chat not found" in er.description:
                logger.error(f"User not found: {row.User}")
            else:
                logger.error(
                    f"Unknown error when getting user info for {row.User}: {er}"
                )
            continue
        ret.append((first_name, row.value))
    return ret


async def _handle_impl(
    session: sqlalchemy.orm.Session, message: telebot.types.Message
):
    argument = telebot.util.extract_arguments(typing.cast(str, message.text))
    if len(argument) == 0:
        currency = strings.CREDIT_BOT_DEFAULT_CURRENCY
    else:
        currency = argument

    chat_id = message.chat.id
    leaderboard = await _create_leaderboard(session, chat_id, currency)

    TOP_NUMBER = 5
    best = leaderboard[:TOP_NUMBER]
    worst = leaderboard[TOP_NUMBER:][-TOP_NUMBER:]
    text = f"Больше всего {currency}баллов:\n"
    if len(best) == 0:
        text += "ни у кого!"

    async def concat_values(leaderboard):
        ret = ""
        for first_name, value in leaderboard:
            ret += "{} ➔ {}\n".format(first_name, str(value))
        return ret

    text += await concat_values(best)

    if len(worst) != 0:
        text += f"Меньше всего {currency}баллов:\n"
        text += await concat_values(worst)
    await bot.reply_to(message, text)


async def handle(message: telebot.types.Message):
    try:
        logger.info(
            f"[handle] /rank: {create_who_triggered_str(message)} text={message.text}"
        )
        with database.Session.begin() as session:
            await _handle_impl(session, message)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
