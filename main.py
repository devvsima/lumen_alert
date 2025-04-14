import asyncio

from dsbot.run import start_discord_bot
from tgbot.run import start_telegram_bot


async def main():
    discord_task = asyncio.create_task(start_discord_bot())
    telegram_task = asyncio.create_task(start_telegram_bot())

    await asyncio.gather(discord_task, telegram_task)


if __name__ == "__main__":
    asyncio.run(main())
