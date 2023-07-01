import random
import typing

START_PRIVATE_CHAT = "Добавь меня в чат чтобы отслеживать баллы"
SELF_LIKE = "Запрещено! Немедленно прекратите! Штраф 1000 рублей."
CREDIT_MINUS_ITSELF = "Ok Idiot, You lost it"

_PLUS_CREDIT_MESSAGES = [
    "Родина гордится тобой! +{} {}{}!",
    "Отличная работа! +{} {}{}!",
    "Все дальше от буржуйства! +{} {}{}!",
    "Так когда-то и Раст начнешь изучать! +{} {}{}!",
    "Один миска си плюс плюс и аниме жена! +{} {}{}! 打!",
]
_MINUS_CREDIT_MESSAGES = [
    "Позор! {} {}{}!",
    "Прекратите. {} {}{}.",
    "Так и буржуем можно стать. {} {}{}.",
    "Плохо! {} {}{}.",
    "丟人現眼. Отобрать аниме жена. {} {}{}.",
]


def _get_declination(number: int, cases: typing.List[str]) -> str:
    last_digit = abs(number) % 10
    last_ten = abs(number) % 100
    if last_digit == 1 and (last_ten < 10 or last_ten > 20):
        return cases[0]
    if last_digit > 1 and last_digit <= 4 and (last_ten < 10 or last_ten > 20):
        return cases[1]
    return cases[2]


def _get_points_message_for_points(points: int) -> str:
    return _get_declination(points, ["балл", "балла", "баллов"])


def get_string_for_points(currency: str, points: int) -> str:
    if points > 0:
        messages = _PLUS_CREDIT_MESSAGES
    else:
        messages = _MINUS_CREDIT_MESSAGES
    message = random.choice(messages)

    return message.format(points, currency, _get_points_message_for_points(points))
