import random
import typing

SELF_LIKE = "Запрещено! Немедленно прекратите! Штраф 1000 рублей."
CREDIT_BOT_DEFAULT_CURRENCY = "вектор"

_PLUS_CREDIT_MESSAGES = [
    "Оп! +{} {}{}!",
]
_MINUS_CREDIT_MESSAGES = [
    "Не оп. {} {}{}!",
]


def _get_declination(number: int, cases: typing.List[str]) -> str:
    last_digit = abs(number) % 10
    last_ten = abs(number) % 100
    if last_digit == 1 and (last_ten < 10 or last_ten > 20):
        return cases[0]
    if last_digit > 1 and last_digit <= 4 and (last_ten < 10 or last_ten > 20):
        return cases[1]
    return cases[2]


def get_points_message_for_points(points: int) -> str:
    return _get_declination(points, ["балл", "балла", "баллов"])


def get_holders_message_for_holders(holders):
    return _get_declination(holders, ["держатель", "держателя", "держателей"])


def get_string_for_points(currency: str, points: int) -> str:
    if points > 0:
        messages = _PLUS_CREDIT_MESSAGES
    else:
        messages = _MINUS_CREDIT_MESSAGES
    message = random.choice(messages)

    return message.format(points, currency, get_points_message_for_points(points))
