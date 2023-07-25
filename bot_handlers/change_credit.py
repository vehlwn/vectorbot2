from datetime import datetime
from sqlalchemy import select
import re
import sqlalchemy.orm
import telebot
import traceback

from async_bot import bot
from logger import logger, create_who_triggered_str
from logger import logger
from models import (
    Currency,
    Point,
    TokenBucket,
    User,
    TokenBucket,
    garbage_collect_currencies,
)
from settings import settings
import database
import strings


def _get_or_create_currency(
    session: sqlalchemy.orm.Session, currency: str
) -> Currency:
    ret = session.scalars(select(Currency).where(Currency.name == currency)).first()
    if ret is None:
        new = Currency(name=currency)
        logger.info(f"Creating new currency: {new}")
        session.add(new)
        ret = new
    return ret


def _get_or_create_user(session: sqlalchemy.orm.Session, chat_id: int, user_id: int):
    ret = session.scalars(
        select(User).where((User.chat_id == chat_id) & (User.user_id == user_id))
    ).first()
    if ret is None:
        ret = User(chat_id=chat_id, user_id=user_id)
        logger.info(f"Creating new user: {ret}")
        session.add(ret)
    return ret


def _check_token_bucket_limit(
    session: sqlalchemy.orm.Session,
    chat_id: int,
    user_id: int,
    value: int,
) -> bool:
    user_row = _get_or_create_user(session, chat_id, user_id)
    if user_row.token_bucket is None:
        new = TokenBucket(
            current_size=settings.POINTS_BURST_SIZE, last_refill=datetime.utcnow()
        )
        logger.info(f"Creating new token bucket: {new}")
        user_row.token_bucket = new
    ret = user_row.token_bucket.consume(abs(value))
    logger.info(f"Consumed token bucket: {user_row.token_bucket}")
    return ret


def _increment_credit(
    session: sqlalchemy.orm.Session,
    chat_id: int,
    user_id: int,
    currency: str,
    value: int,
):
    currency_row = _get_or_create_currency(session, currency)
    user_row = _get_or_create_user(session, chat_id, user_id)
    point_row = session.scalars(
        select(Point).where(
            (Point.user_id == user_row.id) & (Point.currency == currency_row)
        )
    ).first()
    if point_row is None:
        logger.info(f"Creating new point for user {user_row}")
        user_row.points.append(Point(value=value, currency=currency_row))
    else:
        logger.info(f"Updating points: {point_row}")
        point_row.value += value
        if point_row.value == 0:
            logger.info(f"Deleting zero value: {point_row}")
            session.delete(point_row)
            garbage_collect_currencies(session)


def _parse_credit_line(text: str):
    match = re.search(settings.CHANGE_CREDIT_PATTERN, text)
    if match is None:
        logger.info("Unexpected! Regex does not match")
        return None
    currency = match[3]
    sign = +1 if match[1] == "+" else -1
    points = int(match[2])
    points = sign * points
    return points, currency


async def _handle_impl(message: telebot.types.Message):
    if (
        message.reply_to_message is None
        and message.from_user.id != settings.SUPER_ADMIN_ID
    ):
        return

    if message.text is None:
        return

    parsed_result = _parse_credit_line(message.text)
    if parsed_result is None:
        return

    (points, currency) = parsed_result

    if message.reply_to_message is None:
        whom_to_credit = message.from_user
    else:
        whom_to_credit = message.reply_to_message.from_user

    if (
        message.from_user.id != settings.SUPER_ADMIN_ID
        and message.from_user.id == whom_to_credit.id
    ):
        text = strings.SELF_LIKE
        logger.info("Self like")
        await bot.reply_to(message, text)
        return
    else:
        text = strings.get_string_for_points(currency, points)

    if len(currency) > settings.MAX_CURRENCY_LEN:
        await bot.reply_to(
            message,
            f"Слишком длинно! Лимит на длину - {settings.MAX_CURRENCY_LEN} символов!",
        )
        return

    if (
        message.from_user.id != settings.SUPER_ADMIN_ID
        and abs(points) > settings.POINTS_BURST_SIZE
    ):
        await bot.reply_to(
            message,
            "Слишком много! Лимит на изменение - {} {}баллов!".format(
                settings.POINTS_BURST_SIZE, currency
            ),
        )
        return

    with database.Session.begin() as session:
        if (
            message.from_user.id != settings.SUPER_ADMIN_ID
            and not _check_token_bucket_limit(
                session,
                message.chat.id,
                message.from_user.id,
                points,
            )
        ):
            await bot.reply_to(
                message,
                "Слишком быстро! Лимит на изменение - {} баллов/мин!".format(
                    round(settings.POINTS_REFILL_RATE * 60.0, 2)
                ),
            )
            return
        logger.info(
            f"{whom_to_credit.id=} {whom_to_credit.first_name} {points=} {currency=}"
        )
        _increment_credit(
            session, message.chat.id, whom_to_credit.id, currency, points
        )

    if message.reply_to_message is None:
        reply_to_message = message
    else:
        reply_to_message = message.reply_to_message
    await bot.reply_to(reply_to_message, text)


async def handle(message: telebot.types.Message):
    try:
        logger.info(
            f"[handle] change_credit: {create_who_triggered_str(message)} text={message.text}"
        )
        await _handle_impl(message)
    except Exception as er:
        await bot.reply_to(message, f"Error: {er}")
        traceback.print_exc()
