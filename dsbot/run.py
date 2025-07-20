from data.config import discord_bot
from utils.logging import logger

from .handlers import dsbot


async def start_discord_bot():
    logger.log("BOT", "~ Discord bot startup")
    try:
        await dsbot.start(discord_bot.TOKEN)
    except Exception as e:
        logger.error(f"Discord bot error: {e}")
        raise
    finally:
        logger.log("BOT", "~ Discord bot shutdown")
        if not dsbot.is_closed():
            await dsbot.close()
