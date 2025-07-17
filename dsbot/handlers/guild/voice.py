from data.config import discord_bot
from dsbot.loader import dsbot
from tgbot.handlers.bot_utils import send_telegram_message
from utils.logging import logger


@dsbot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != discord_bot.SERVER_ID:
        return

    if before.channel is None and after.channel is not None:
        # Отладочная информация о member
        logger.info(f"=== MEMBER DEBUG INFO ===")
        logger.info(f"Type: {type(member)}")
        logger.info(f"Dir: {dir(member)}")
        logger.info(f"Dict: {member.__dict__ if hasattr(member, '__dict__') else 'No __dict__'}")

        # Основные атрибуты
        logger.info(f"ID: {member.id}")
        logger.info(f"Name: {member.name}")
        logger.info(f"Display name: {member.display_name}")
        logger.info(f"Discriminator: {member.discriminator}")
        logger.info(f"Avatar URL: {member.avatar.url if member.avatar else 'No avatar'}")
        logger.info(f"Created at: {member.created_at}")
        logger.info(f"Joined at: {member.joined_at}")
        logger.info(f"Status: {member.status}")
        logger.info(f"Activity: {member.activity}")
        logger.info(f"Roles: {[role.name for role in member.roles]}")
        logger.info(f"Top role: {member.top_role.name}")
        logger.info(f"Is bot: {member.bot}")
        logger.info(f"Is premium: {member.premium}")
        logger.info(f"Guild permissions: {member.guild_permissions}")
        logger.info(f"=========================")

        text = f"<code>{member.name}</code> joined the voice channel - {after.channel.name}"
        logger.info(f"TgUser {member.name} joined voice channel {after.channel.name}")
        await send_telegram_message(text)
