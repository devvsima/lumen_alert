from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from tgbot.routers import user_router as router
from tgbot.text import message_text as mt


@router.message(Command("help"), StateFilter(None))
async def _help_command(message: types.Message) -> None:
    """Дает описание бота"""
    help_text = f"""{mt.INFO}

**📊 Dashboard Commands:**
• `/create_dashboard` - Create new voice channels dashboard
• `/update_dashboards` - Force update all dashboards
• `/remove_dashboard` - Remove dashboard (reply to dashboard message)
• `/list_dashboards` - Show all active dashboards in this chat

**� Voice Monitoring:**
• `/voice_stats` - Show detailed voice channels statistics
• `/clear_voice_channels` - Clear all voice channel records (admin)

**�🔊 Voice Channel Features:**
• Real-time monitoring of Discord voice channels
• Automatic dashboard updates when users join/leave
• Shows current users in each voice channel
• Total users count

**ℹ️ Dashboard automatically updates when:**
• Someone joins a voice channel
• Someone leaves a voice channel  
• Someone switches between channels"""

    await message.answer(help_text, parse_mode="Markdown")
