import asyncio


from async_bot import bot
from logger import logger
import bot_handlers
import models


async def main():
    models.create_all()
    logger.info("DB models created")
    bot_handlers.setup()
    logger.info("Bot is listening")
    await bot.polling()


if __name__ == "__main__":
    asyncio.run(main())
