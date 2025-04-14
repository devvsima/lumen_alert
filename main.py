import asyncio

from aiogram.methods import DeleteWebhook

from data.config import SKIP_UPDATES
from disbot.run import start_discord_bot
from loader import bot, dp
from tgbot.handlers import setup_handlers
from tgbot.middlewares import setup_middlewares
from tgbot.others.commands import set_default_commands
from utils.logging import logger


async def on_startup() -> None:
    await set_default_commands()
    logger.log("BOT", "~ Bot startup")


async def on_shutdown() -> None:
    logger.log("BOT", "~ Bot shutting down...")


async def start_telegram_bot():
    await on_startup(dp)
    try:
        await dp.start_polling()
    finally:
        await on_shutdown(dp)


async def main():
    setup_middlewares(dp)
    setup_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot(DeleteWebhook(drop_pending_updates=SKIP_UPDATES))
    # Создание задач для каждого бота и aiohttp сервера
    discord_task = asyncio.create_task(start_discord_bot())
    telegram_task = asyncio.create_task(start_telegram_bot())

    # Ожидание завершения всех задач
    await asyncio.gather(discord_task, telegram_task)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
