import telebot.asyncio_filters

from async_bot import bot
from logger import logger


class MatchBotUsernameFilter(telebot.asyncio_filters.SimpleCustomFilter):
    key = "match_bot_username"

    def __init__(self, bot_name: str) -> None:
        super().__init__()
        self.bot_name = bot_name

    async def check(self, message: telebot.types.Message) -> bool:
        text = message.text or ""
        words = text.split(maxsplit=1)
        full_command = words[0].split("@")
        if len(full_command) >= 2:
            bot_username = full_command[1]
            return bot_username == self.bot_name
        return True


async def register_custom_filters():
    me = await bot.get_me()
    if me.username is None:
        raise RuntimeError("Bot must have username")
    bot_name = me.username
    logger.debug(f"Bot username = {bot_name}")
    bot.add_custom_filter(MatchBotUsernameFilter(bot_name))
