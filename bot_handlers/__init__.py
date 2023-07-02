from async_bot import bot
from . import ping, get_my_id, credits, rank, balls, change_credit


def register_all():
    bot.register_message_handler(ping.handle, commands=["ping"])
    bot.register_message_handler(get_my_id.handle, commands=["get_my_id"])
    bot.register_message_handler(credits.handle, commands=["credits"])
    bot.register_message_handler(rank.handle, commands=["rank"])
    bot.register_message_handler(balls.handle, commands=["balls"])
    bot.register_message_handler(change_credit.handle)
