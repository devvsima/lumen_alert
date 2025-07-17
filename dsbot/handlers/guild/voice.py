from data.config import discord_bot
from database.connect import async_session
from database.services.ds_users import DsUser
from database.services.voice_channel import VoiceChannelUser
from dsbot.loader import dsbot
from tgbot.business.voice_update_alert import send_alert_to_users
from tgbot.business.voice_update_dashboard import update_all_dashboards
from utils.logging import logger


@dsbot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != discord_bot.SERVER_ID:
        return

    async with async_session() as session:
        # Создаем или обновляем пользователя Discord
        await DsUser.get_or_create(
            session,
            user_id=member.id,
            display_name=member.display_name,
            name=member.name,
        )

        # Если пользователь присоединился к каналу
        if before.channel is None and after.channel is not None:
            await VoiceChannelUser.add_user_to_channel(
                session,
                user_id=member.id,
                user_name=member.name,
                display_name=member.display_name,
                channel_id=after.channel.id,
                channel_name=after.channel.name
            )
            
            text = f"<code>{member.display_name}</code> joined the voice channel - {after.channel.name}"
            logger.info(f"User {member.display_name} joined voice channel {after.channel.name}")
            await send_alert_to_users(text=text)

        # Если пользователь покинул канал
        elif before.channel is not None and after.channel is None:
            await VoiceChannelUser.remove_user_from_all_channels(session, member.id)
            
            text = f"<code>{member.display_name}</code> left the voice channel - {before.channel.name}"
            logger.info(f"User {member.display_name} left voice channel {before.channel.name}")
            await send_alert_to_users(text=text)

        # Если пользователь переключился между каналами
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            await VoiceChannelUser.add_user_to_channel(
                session,
                user_id=member.id,
                user_name=member.name,
                display_name=member.display_name,
                channel_id=after.channel.id,
                channel_name=after.channel.name
            )
            
            text = f"<code>{member.display_name}</code> switched from {before.channel.name} to {after.channel.name}"
            logger.info(f"User {member.display_name} switched from {before.channel.name} to {after.channel.name}")
            await send_alert_to_users(text=text)

    # Обновляем все дашборды после любого изменения
    await update_all_dashboards()
