from data.config import discord_bot
from dsbot.loader import discord_client
from tgbot.handlers.bot_utils import send_telegram_message
from utils.logging import logger


@discord_client.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != discord_bot.SERVER_ID:
        return

    if before.channel is None and after.channel is not None:
        text = f"<code>{member.name}</code> joined the voice channel - {after.channel.name}"
        logger.info(f"User {member.name} joined voice channel {after.channel.name}")
        await send_telegram_message(text)


async def start_discord_bot():
    logger.info("Starting Discord bot...")
    await discord_client.start(discord_bot.TOKEN)
