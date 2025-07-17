from data.config import discord_bot
from database.connect import async_session
from database.services.ds_users import DsUser
from dsbot.loader import dsbot
from tgbot.business.voice_update_alert import send_alert_to_users
from utils.logging import logger


@dsbot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != discord_bot.SERVER_ID:
        return

    if before.channel is None and after.channel is not None:
        async with async_session() as session:
            await DsUser.get_or_create(
                session,
                user_id=member.id,
                display_name=member.display_name,
                name=member.name,
            )

        text = f"<code>{member.name}</code> joined the voice channel - {after.channel.name}"
        logger.info(f"TgUser {member.name} joined voice channel {after.channel.name}")
        await send_alert_to_users(text=text)
