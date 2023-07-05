import telebot.async_telebot

from settings import settings

bot = telebot.async_telebot.AsyncTeleBot(settings.BOT_TOKEN)
