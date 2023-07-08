import asyncio


from async_bot import bot
from logger import logger
import bot_handlers
import models


async def main():
    await bot_handlers.register_all()
    logger.info("Bot handles registered")
    models.create_all()
    logger.info("DB models created")
    logger.info("Bot is listening")
    await bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(main())
