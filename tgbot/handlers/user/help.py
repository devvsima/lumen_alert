from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from tgbot.routers import user_router as router
from tgbot.text import message_text as mt
from tgbot.loader import _


@router.message(Command("help"), StateFilter(None))
async def _help_command(message: types.Message) -> None:
    """Дает описание бота"""
    help_text = f"""{mt.INFO}

{_("📊 Команды дашборда:")}
• `/create_dashboard` - {_("создать дашборд голосовых каналов")}
• `/update_dashboards` - {_("принудительно обновить дашборды")}
• `/remove_dashboard` - {_("удалить дашборд ответом на его сообщение")}
• `/list_dashboards` - {_("показать дашборд текущего чата")}

{_("🎙️ Мониторинг голосовых каналов:")}
• `/voice_stats` - {_("показать статистику голосовых каналов")}
• `/clear_voice_channels` - {_("очистить записи голосовых каналов")}

{_("🔊 Возможности:")}
• {_("мониторинг голосовых каналов в реальном времени")}
• {_("автоматическое обновление дашбордов")}
• {_("список пользователей в каждом канале")}
• {_("общее количество пользователей")}

{_("ℹ️ Дашборд обновляется при входе, выходе и переходе между каналами.")}"""

    await message.answer(help_text, parse_mode="HTML")
