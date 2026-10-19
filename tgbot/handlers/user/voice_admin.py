from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from sqlalchemy import delete

from database.connect import async_session
from database.models.voice_channel import VoiceChannelUserModel
from database.services.voice_channel import VoiceChannelUser
from tgbot.business.voice_update_dashboard import update_all_dashboards
from tgbot.routers import user_router as router
from tgbot.loader import _


@router.message(Command("clear_voice_channels"), StateFilter(None))
async def _clear_voice_channels_command(message: types.Message) -> None:
    """Очищает все записи о пользователях в голосовых каналах (админ команда)"""
    try:
        # TODO: Добавить проверку прав администратора

        async with async_session() as session:
            # Получаем всех пользователей перед очисткой
            users_before = await VoiceChannelUser.get_all_users_in_channels(session)
            count_before = len(users_before)

            # Очищаем всех пользователей
            await session.execute(delete(VoiceChannelUserModel))
            await session.commit()

        # Обновляем дашборды
        await update_all_dashboards()

        await message.answer(
            _("✅ Удалено пользователей из голосовых каналов: {count}. Дашборды обновлены.").format(
                count=count_before
            )
        )

    except Exception as e:
        await message.answer(_("❌ Не удалось очистить голосовые каналы: {error}").format(error=str(e)))


@router.message(Command("voice_stats"), StateFilter(None))
async def _voice_stats_command(message: types.Message) -> None:
    """Показывает статистику по голосовым каналам"""
    try:
        async with async_session() as session:
            users_in_channels = await VoiceChannelUser.get_all_users_in_channels(session)

        if not users_in_channels:
            await message.answer(
                _("📊 <b>Статистика голосовых каналов</b>\n\n📭 Сейчас нет пользователей.")
            )
            return

        # Группируем пользователей по каналам
        channels_stats = {}
        total_users = 0

        for user in users_in_channels:
            if user.channel_name not in channels_stats:
                channels_stats[user.channel_name] = {
                    'count': 0,
                    'users': []
                }
            channels_stats[user.channel_name]['count'] += 1
            channels_stats[user.channel_name]['users'].append({
                'name': user.display_name,
                'joined': user.joined_at
            })
            total_users += 1

        # Формируем статистику
        text = _("📊 <b>Статистика голосовых каналов</b>\n\n")

        for channel_name, stats in channels_stats.items():
            text += _("🎙️ <b>{channel}</b>: {count} пользователей\n").format(
                channel=channel_name, count=stats["count"]
            )
            for user in stats['users']:
                joined_time = user['joined'].strftime('%H:%M')
                text += _("  👤 {name} (вошёл в {time})\n").format(
                    name=user["name"], time=joined_time
                )
            text += "\n"

        text += _("📈 <b>Всего пользователей: {count}</b>\n").format(count=total_users)
        text += _("🔊 <b>Активных каналов: {count}</b>").format(count=len(channels_stats))

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(_("❌ Не удалось получить статистику: {error}").format(error=str(e)))
