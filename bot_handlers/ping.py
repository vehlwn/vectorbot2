import telebot

from async_bot import bot


async def handle(message: telebot.types.Message):
    await bot.reply_to(message, text="I'm alive!")
