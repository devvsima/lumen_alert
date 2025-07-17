from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from sqlalchemy import delete

from database.connect import async_session
from database.models.voice_channel import VoiceChannelUserModel
from database.services.voice_channel import VoiceChannelUser
from tgbot.business.voice_update_dashboard import update_all_dashboards
from tgbot.routers import user_router as router


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
        
        await message.answer(f"✅ Cleared {count_before} users from voice channels. All dashboards updated.")
        
    except Exception as e:
        await message.answer(f"❌ Error clearing voice channels: {str(e)}")


@router.message(Command("voice_stats"), StateFilter(None))
async def _voice_stats_command(message: types.Message) -> None:
    """Показывает статистику по голосовым каналам"""
    try:
        async with async_session() as session:
            users_in_channels = await VoiceChannelUser.get_all_users_in_channels(session)
            
        if not users_in_channels:
            await message.answer("📊 **Voice Channels Statistics**\n\n📭 No users currently in voice channels")
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
        text = "📊 **Voice Channels Statistics**\n\n"
        
        for channel_name, stats in channels_stats.items():
            text += f"🎙️ **{channel_name}**: {stats['count']} users\n"
            for user in stats['users']:
                joined_time = user['joined'].strftime('%H:%M')
                text += f"  👤 {user['name']} (joined at {joined_time})\n"
            text += "\n"
        
        text += f"📈 **Total users in voice channels: {total_users}**\n"
        text += f"🔊 **Active channels: {len(channels_stats)}**"
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Error getting voice stats: {str(e)}")
