from html import escape

from database.connect import async_session
from database.services.ds_users import DsUser
from database.services.voice_channel import VoiceChannelUser
from database.services.sources import DiscordSource
from dsbot.loader import dsbot
from tgbot.business.voice_update_alert import send_join_alert, send_leave_alert, send_switch_alert
from tgbot.business.voice_update_dashboard import update_all_dashboards
from utils.logging import logger


@dsbot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        async with async_session() as session:
            settings = await DiscordSource.get_guild_settings(session, member.guild.id)
        if settings is None or settings.ignore_bots:
            return

    if before.channel is None and after.channel is None:
        return

    async with async_session() as session:
        voice_channels = [
            channel for channel in member.guild.channels if channel.type.name == "voice"
        ]
        await DiscordSource.sync_guild(
            session, member.guild.id, member.guild.name, voice_channels
        )
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
                channel_name=after.channel.name,
            )

            settings = await DiscordSource.get_guild_settings(session, member.guild.id)
            text = settings.join_template.format(
                user=f"<code>{escape(member.display_name)}</code>",
                channel=escape(after.channel.name),
                server=escape(member.guild.name),
            )
            logger.info(f"User {member.display_name} joined voice channel {after.channel.name}")
            await send_join_alert(text=text, guild_id=member.guild.id, channel_id=after.channel.id)

        # Если пользователь покинул канал
        elif before.channel is not None and after.channel is None:
            await VoiceChannelUser.remove_user_from_all_channels(session, member.id)

            settings = await DiscordSource.get_guild_settings(session, member.guild.id)
            text = settings.leave_template.format(
                user=f"<code>{escape(member.display_name)}</code>",
                channel=escape(before.channel.name),
                server=escape(member.guild.name),
            )
            logger.info(f"User {member.display_name} left voice channel {before.channel.name}")
            await send_leave_alert(text=text, guild_id=member.guild.id, channel_id=before.channel.id)

        # Если пользователь переключился между каналами
        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel != after.channel
        ):
            await VoiceChannelUser.add_user_to_channel(
                session,
                user_id=member.id,
                user_name=member.name,
                display_name=member.display_name,
                channel_id=after.channel.id,
                channel_name=after.channel.name,
            )

            settings = await DiscordSource.get_guild_settings(session, member.guild.id)
            text = settings.switch_template.format(
                user=f"<code>{escape(member.display_name)}</code>",
                from_channel=escape(before.channel.name),
                channel=escape(after.channel.name),
                server=escape(member.guild.name),
            )
            logger.info(
                f"User {member.display_name} switched from {before.channel.name} to {after.channel.name}"
            )
            await send_switch_alert(
                text=text,
                guild_id=member.guild.id,
                before_channel_id=before.channel.id,
                after_channel_id=after.channel.id,
            )

    # Обновляем все дашборды после любого изменения
    await update_all_dashboards()
