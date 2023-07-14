import random
import typing

SELF_LIKE = "Запрещено! Немедленно прекратите! Штраф 1000 рублей."
CREDIT_BOT_DEFAULT_CURRENCY = "вектор"

_PLUS_CREDIT_MESSAGES = [
    "Родина гордится тобой! +{} {}{}!",
    "Отличная работа! +{} {}{}!",
    "Все дальше от буржуйства! +{} {}{}!",
    "Так когда-то и Раст начнешь изучать! +{} {}{}!",
    "Один миска си плюс плюс и аниме жена! +{} {}{}! 打!",
    "Опачки! +{} {}{}!",
    "Ты превратился в легендарного школьника! +{} {}{}!",
    "Что за хуйня, я не ожидал такого! +{} {}{}!",
    "Что за фигня, я ничего не понял! +{} {}{}!",
    "Что за пиздец, я не знаю, что делать! +{} {}{}!",
    "Ты настоящий человек-паук! +{} {}{}!",
    "Твоя преданность партии заслуживает похвалы! +{} {}{}!",
    "Прекрасно сделано! +{} {}{}! Так держать!",
    "Выдрячная работа! +{} {}{}!",
    "С тобой коммунизм не за горами! +{} {}{}!",
    "Дай ему медаль! +{} {}{}!",
    "Император будет доволен! +{} {}{}!",
    "Сталин бы расстрелял от гордости! +{} {}{}!",
    "Ты продолжаешь дело Великого Вождя! +{} {}{}!",
    "Новый уровень достигнут! +{} {}{}! Теперь можешь вызывать Покемонов!",
    "Матрица гордится тобой! +{} {}{}!",
]
_MINUS_CREDIT_MESSAGES = [
    "Позор! {} {}{}!",
    "Прекратите. {} {}{}.",
    "Так и буржуем можно стать. {} {}{}.",
    "Плохо! {} {}{}.",
    "丟人現眼. Отобрать аниме жена. {} {}{}.",
    "Это просто печально. {} {}{}.",
    "Позорище! {} {}{}.",
    "Стыд и срам! {} {}{}.",
    "Ну что, опять провал? {} {}{}.",
    "Никакого уважения! {} {}{}.",
    "Это какой-то кошмар. {} {}{}.",
    "Надоело! {} {}{}.",
    "Серьезно? {} {}{}.",
    "А ну-ка, давайте без этого! {} {}{}.",
    "Лучше бы молчали! {} {}{}.",
    "Ты обесчестишь свою семью. {} {}{}.",
    "Ну что, мастер шуток? {} {}{}? Я бы на твоем месте задумался.",
    "Ох, уж эти шутники! {} {}{}, прекратите уже!",
    "Не в этот раз, {} {}{}!",
    "Даже не знаю, что сказать, {} {}{}. Не ожидал такого.",
    "Как можно было такое сделать, {} {}{}? Серьезно?",
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
