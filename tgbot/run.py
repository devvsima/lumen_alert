import asyncio

from aiogram.methods import DeleteWebhook

from data.config import telegram_bot
from tgbot.handlers import setup_handlers
from tgbot.loader import bot, dp
from tgbot.middlewares import setup_middlewares
from tgbot.others.commands import set_default_commands
from utils.logging import logger


async def on_startup() -> None:
    await set_default_commands()
    logger.log("BOT", "~ Telegram bot startup")


async def on_shutdown() -> None:
    logger.log("BOT", "~ Telegram bot shutting down...")


async def start_telegram_bot():
    setup_middlewares(dp)
    setup_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot(DeleteWebhook(drop_pending_updates=telegram_bot.SKIP_UPDATES))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_telegram_bot())
