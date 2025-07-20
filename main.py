import asyncio
import signal
import sys

from dsbot.run import start_discord_bot
from tgbot.run import start_telegram_bot
from utils.logging import logger

shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    logger.log("BOT", f"Received signal {sig}, shutting down...")
    shutdown_event.set()


async def main():
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        discord_task = asyncio.create_task(start_discord_bot())
        telegram_task = asyncio.create_task(start_telegram_bot())

        # Ждем завершения или сигнал остановки
        done, pending = await asyncio.wait(
            [discord_task, telegram_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Отменяем незавершенные задачи
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        logger.log("BOT", "Application shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.log("BOT", "Received KeyboardInterrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        sys.exit(0)
