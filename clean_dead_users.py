import argparse
from sqlalchemy import select, delete
import asyncio
from telebot.asyncio_helper import ApiTelegramException

from async_bot import bot
from logger import logger
from models import User
import database


async def main():
    parser = argparse.ArgumentParser(
        description="Helper script to prune dead users from the database",
    )
    parser.add_argument(
        "--dry-run", help="Do not modify database", action="store_true"
    )
    args = parser.parse_args()

    with database.Session.begin() as session:
        for row in session.execute(select(User.user_id).distinct()):
            try:
                await bot.get_chat(row.user_id)
            except ApiTelegramException as er:
                if "chat not found" in er.description:
                    logger.error(f"User not found: {row.user_id}")
                    if args.dry_run:
                        continue
                    result = session.execute(
                        delete(User).where(User.user_id == row.user_id)
                    )
                    logger.info(f"Deleted {result.rowcount} rows")


if __name__ == "__main__":
    asyncio.run(main())
