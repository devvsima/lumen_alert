from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from tgbot.business.voice_update_dashboard import create_new_dashboard, update_all_dashboards
from tgbot.loader import _
from tgbot.routers import user_router as router
from tgbot.text import message_text as mt


@router.message(Command("create_dashboard"), StateFilter(None))
async def _create_dashboard_command(message: types.Message) -> None:
    """Создает дашборд с информацией о голосовых каналах"""
    try:
        await message.answer(_("📊 Создаём дашборд голосовых каналов..."))
        dashboard_message_id = await create_new_dashboard(message.chat.id)
        await message.answer(
            _("✅ Дашборд успешно создан. ID сообщения: {message_id}").format(
                message_id=dashboard_message_id
            )
        )
    except Exception as e:
        await message.answer(_("❌ Не удалось создать дашборд: {error}").format(error=str(e)))


@router.message(Command("update_dashboards"), StateFilter(None))
async def _update_dashboards_command(message: types.Message) -> None:
    """Принудительно обновляет все дашборды"""
    try:
        await message.answer(_("🔄 Обновляем все дашборды..."))
        await update_all_dashboards()
        await message.answer(_("✅ Все дашборды обновлены."))
    except Exception as e:
        await message.answer(_("❌ Не удалось обновить дашборды: {error}").format(error=str(e)))
