import typing
from sqlalchemy import select
import re
import telebot

from async_bot import bot
from logger import logger
from models import Currency, Point, User
import database
import settings
import strings


@bot.message_handler(commands=["ping"])
async def ping_handler(message: telebot.types.Message):
    await bot.reply_to(message, text="I'm alive!")


@bot.message_handler(commands=["get_my_id"])
async def get_my_id_handler(message: telebot.types.Message):
    await bot.reply_to(message, text=str(message.from_user.id))


def _is_reply(message: telebot.types.Message):
    return message.reply_to_message is not None


def _increment_credit(chat_id: int, user_id: int, currency: str, value: int):
    with database.Session.begin() as session:
        currency_row = session.scalars(
            select(Currency).where(Currency.name == currency)
        ).first()
        if currency_row is None:
            logger.info(f"Creating new currency: {currency}")
            session.add(Currency(name=currency))

        currency_row = session.scalars(
            select(Currency).where(Currency.name == currency)
        ).one()
        user_row = session.scalars(
            select(User).where((User.chat_id == chat_id) & (User.user_id == user_id))
        ).first()
        if user_row is None:
            new_user = User(chat_id=chat_id, user_id=user_id)
            logger.info(f"Creating new user: {new_user}")
            new_point = Point(value=value, currency_id=currency_row.id)
            logger.info(f"Creating new point for new user: {new_point}")
            new_user.points.append(new_point)
            session.add(new_user)
        else:
            point_row = session.scalars(
                select(Point).where(
                    (Point.user_id == user_row.id)
                    & (Point.currency_id == currency_row.id)
                )
            ).first()
            if point_row is None:
                logger.info(f"Creating new point for existing user: {user_row}")
                session.add(
                    Point(
                        value=value,
                        currency_id=currency_row.id,
                        user_id=user_row.id,
                    )
                )
            else:
                logger.info(f"Updating points: {point_row.value}")
                point_row.value += value


@bot.message_handler(func=_is_reply)
async def change_credit_handler(message: telebot.types.Message):
    logger.info("change_credit_handler")
    if message.reply_to_message is None:
        raise RuntimeError("Unexpected! reply_to_message must not be None!")
    if message.text is None:
        raise RuntimeError("Unexpected! message.text must not be None!")

    user = message.reply_to_message.from_user
    if user.is_bot:
        logger.info("Reply to bot")
        return

    if (
        message.chat.type != "group"
        and message.from_user.id != settings.SUPER_ADMIN_ID
    ):
        await bot.reply_to(message, strings.START_PRIVATE_CHAT)
        return

    match = re.match(settings.CHANGE_CREDIT_PATTERN, message.text)
    if match is None:
        logger.info("Regex does not match")
        return

    currency = match[3]
    if len(currency) > settings.MAX_CURRENCY_LEN:
        await bot.reply_to(
            message,
            f"Слишком длинно! Лимит на длину - {settings.MAX_CURRENCY_LEN} символов!",
        )
        return
    sign = +1 if match[1] == "+" else -1
    if len(match[2]) > 0:
        points = int(match[2])
    else:
        points = 1

    if (
        message.from_user.id != settings.SUPER_ADMIN_ID
        and abs(points) > settings.DELTA_LIMIT
    ):
        await bot.reply_to(
            message,
            f"Слишком много! Лимит на изменение - {settings.DELTA_LIMIT} {currency}баллов!",
        )
        return

    points = sign * points
    if (
        message.from_user.id != settings.SUPER_ADMIN_ID
        and message.from_user.id == user.id
    ):
        if points > 0:
            text = strings.SELF_LIKE
        else:
            logger.info(f"{user.id=} {user.first_name=} {points=} {currency=}")
            text = strings.CREDIT_MINUS_ITSELF
    else:
        logger.info(f"{user.id=} {user.first_name=} {points=} {currency=}")
        text = strings.get_string_for_points(currency, points)
    _increment_credit(message.chat.id, user.id, currency, points)
    await bot.reply_to(message.reply_to_message, text)


def _get_credits_string(chat_id: int, user_id: int) -> str:
    currencies: typing.Dict[str, int] = dict()
    with database.Session.begin() as session:
        result = session.execute(
            select(User, Point, Currency)
            .join(User.points)
            .join(Point.currency)
            .where((User.chat_id == chat_id) & (User.user_id == user_id))
        )
        for row in result:
            currencies[row.Currency.name] = row.Point.value
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


@bot.message_handler(commands=["credits"])
async def redits_handler(message: telebot.types.Message):
    if message.reply_to_message is None:
        await _my_credits_command(message)
        return
    user = message.from_user
    credits = _get_credits_string(message.chat.id, user.id)
    if len(credits) == 0:
        text = "У {user.first_name} нет баллов."
    else:
        text = f"У {user.first_name}:\n{credits}"
    await bot.reply_to(message, text)


def setup():
    pass
