from sqlalchemy import select
import sqlalchemy.orm
import re
import telebot

from async_bot import bot
from logger import logger
from models import Currency, Point, User
import database
import settings
import strings


def _garbage_collect_currencies(session: sqlalchemy.orm.Session):
    result = session.scalars(
        select(Currency).outerjoin(Point).where(Point.currency_id.is_(None))
    )
    logger.info("Deleting orphaned currencies:")
    for row in result:
        logger.info(row)
        session.delete(row)


def _increment_credit(chat_id: int, user_id: int, currency: str, value: int):
    with database.Session.begin() as session:
        currency_expr = select(Currency).where(Currency.name == currency)
        currency_row = session.scalars(currency_expr).first()
        if currency_row is None:
            logger.info(f"Creating new currency: {currency}")
            session.add(Currency(name=currency))

        currency_row = session.scalars(currency_expr).one()
        user_row = session.scalars(
            select(User).where((User.chat_id == chat_id) & (User.user_id == user_id))
        ).first()
        if user_row is None:
            new_user = User(chat_id=chat_id, user_id=user_id)
            logger.info(f"Creating new user: {new_user}")
            new_point = Point(value=value, currency=currency_row)
            logger.info(f"Creating new point for new user: {new_point}")
            new_user.points.append(new_point)
            session.add(new_user)
        else:
            point_row = session.scalars(
                select(Point).where(
                    (Point.user_id == user_row.id) & (Point.currency == currency_row)
                )
            ).first()
            if point_row is None:
                logger.info(f"Creating new point for existing user: {user_row}")
                session.add(
                    Point(
                        value=value,
                        currency=currency_row,
                        user_id=user_row.id,
                    )
                )
            else:
                logger.info(f"Updating points: {point_row.value}")
                point_row.value += value
                if point_row.value == 0:
                    logger.info("Deleting zero value")
                    session.delete(point_row)
                    _garbage_collect_currencies(session)


async def handle(message: telebot.types.Message):
    logger.info("change_credit_handler")
    if (
        message.reply_to_message is None
        and message.from_user.id != settings.SUPER_ADMIN_ID
    ):
        return

    if message.reply_to_message is None:
        whom_to_credit = message.from_user
    else:
        whom_to_credit = message.reply_to_message.from_user

    if message.text is None:
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
        and message.from_user.id == whom_to_credit.id
    ):
        if points > 0:
            text = strings.SELF_LIKE
        else:
            logger.info(
                f"{whom_to_credit.id=} {whom_to_credit.first_name=} {points=} {currency=}"
            )
            text = strings.CREDIT_MINUS_ITSELF
    else:
        logger.info(
            f"{whom_to_credit.id=} {whom_to_credit.first_name=} {points=} {currency=}"
        )
        text = strings.get_string_for_points(currency, points)

    _increment_credit(message.chat.id, whom_to_credit.id, currency, points)

    if message.reply_to_message is None:
        reply_to_message = message
    else:
        reply_to_message = message.reply_to_message
    await bot.reply_to(reply_to_message, text)
