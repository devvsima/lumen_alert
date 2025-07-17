from data.config import discord_bot
from utils.logging import logger

from .handlers import dsbot


async def start_discord_bot():
    logger.log("BOT", "~ Discord bot startup")
    await dsbot.start(discord_bot.TOKEN)
