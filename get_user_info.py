import asyncio
import argparse

from async_bot import bot


async def main():
    parser = argparse.ArgumentParser(
        description="Helper script to get user info by user_id",
    )
    parser.add_argument("user_id", help="Telegram user_id", type=int)
    args = parser.parse_args()
    chat = await bot.get_chat(args.user_id)
    print(chat)


if __name__ == "__main__":
    asyncio.run(main())
