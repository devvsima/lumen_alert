from database.connect import async_session
from database.services.dashboard import Dashboard
from database.services.voice_channel import VoiceChannelUser
from tgbot.keyboards.inline.alert import dashboard_ikb, ds_link_ikb
from tgbot.loader import bot
from utils.logging import logger


async def create_dashboard_text(users_in_channels) -> str:
    """Создает текст для дашборда с информацией о голосовых каналах"""

    if not users_in_channels:
        return "🔊 <b>Voice Channels Dashboard</b>"

    # Группируем пользователей по каналам
    channels_data = {}
    for user in users_in_channels:
        if user.channel_name not in channels_data:
            channels_data[user.channel_name] = []
        channels_data[user.channel_name].append(user.display_name)

    # Формируем текст
    text = ""
    for channel_name, users in channels_data.items():
        text += f"🎙️ <b>{channel_name}</b>\n"
        for user in users:
            text += f"  👤 {user}\n"
        text += "\n"

    text += "🔊 <b>Voice Channels Dashboard</b>\n\n"

    return text


async def update_all_dashboards():
    """Обновляет все активные дашборды"""
    try:
        async with async_session() as session:
            users_in_channels = await VoiceChannelUser.get_all_users_in_channels(session)
            dashboards = await Dashboard.get_all_dashboards(session)

            dashboard_text = await create_dashboard_text(users_in_channels)

            for dashboard in dashboards:
                try:
                    await bot.edit_message_text(
                        chat_id=dashboard.chat_id,
                        message_id=dashboard.message_id,
                        text=dashboard_text,
                        reply_markup=dashboard_ikb(len(users_in_channels)),
                        parse_mode="HTML",
                    )
                    logger.info(
                        f"Dashboard updated for chat {dashboard.chat_id}, message {dashboard.message_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to update dashboard {dashboard.chat_id}:{dashboard.message_id} - {e}"
                    )
                    # Если сообщение не найдено, удаляем дашборд из базы
                    if "message to edit not found" in str(e).lower():
                        await Dashboard.delete_dashboard(
                            session, dashboard.chat_id, dashboard.message_id
                        )
                        logger.info(
                            f"Deleted non-existent dashboard {dashboard.chat_id}:{dashboard.message_id}"
                        )

    except Exception as e:
        logger.error(f"Error in update_all_dashboards: {e}")


async def create_new_dashboard(chat_id: int) -> int:
    """Создает новый дашборд и возвращает message_id"""
    try:
        sent_message = await bot.send_message(
            chat_id=chat_id, text=dashboard_text, reply_markup=ds_link_ikb(), parse_mode="HTML"
        )

        # Сохраняем дашборд в базу данных
        async with async_session() as session:
            users_in_channels = await VoiceChannelUser.get_all_users_in_channels(session)
            dashboard_text = await create_dashboard_text(users_in_channels)

            await Dashboard.create_dashboard(
                session, chat_id=chat_id, message_id=sent_message.message_id
            )

        logger.info(f"New dashboard created for chat {chat_id}, message {sent_message.message_id}")
        return sent_message.message_id

    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise
