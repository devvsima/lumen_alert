import asyncio
from aiogram import Dispatcher, executor
from aiohttp import web

from app import middlewares, filters, handlers
from loader import dp, tgbot
from utils.logging import logger
from app.handlers.user.alert import send_telegram_message

async def on_startup(dp: Dispatcher):
    from app.commands import set_default_commands
    await set_default_commands()
    logger.info("~ Bot_startup")

async def on_shutdown(dp: Dispatcher):
    logger.info("~ Shutting down...")


# Настройка aiohttp для прослушивания входящих запросов (если нужен вебхук)
async def handle_post(request):
    data = await request.json()
    message = data.get('message')
    if message:
        await send_telegram_message(message)
    return web.Response()

app = web.Application()
app.router.add_post('/telegram_webhook', handle_post)

async def start_aiohttp_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=3000)
    await site.start()

async def start_telegram_bot():
    await on_startup(dp)
    try:
        await dp.start_polling()
    finally:
        await on_shutdown(dp)

async def main():
    from app.middlewares import setup_middlewares
    from ds import start_discord_bot
    setup_middlewares(dp)
    
    # Создание задач для каждого бота и aiohttp сервера
    discord_task = asyncio.create_task(start_discord_bot())
    aiohttp_task = asyncio.create_task(start_aiohttp_server())
    telegram_task = asyncio.create_task(start_telegram_bot())

    # Ожидание завершения всех задач
    await asyncio.gather(discord_task, aiohttp_task, telegram_task)

if __name__ == "__main__":
    asyncio.run(main())
