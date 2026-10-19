from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.connect import async_session
from database.services.dashboard import Dashboard
from tgbot.routers import user_router as router
from tgbot.loader import _


@router.message(Command("remove_dashboard"), StateFilter(None))
async def _remove_dashboard_command(message: types.Message) -> None:
    """Удаляет дашборд по reply на сообщение с дашбордом"""
    if not message.reply_to_message:
        await message.answer(_("❌ Ответьте на сообщение дашборда командой /remove_dashboard."))
        return

    try:
        async with async_session() as session:
            success = await Dashboard.delete_dashboard(
                session,
                message.chat.id,
                message.reply_to_message.message_id
            )

        if success:
            await message.answer(_("✅ Дашборд удалён."))
            # Удаляем само сообщение с дашбордом
            try:
                await message.reply_to_message.delete()
            except Exception:
                pass  # Игнорируем ошибки удаления
        else:
            await message.answer(_("❌ Дашборд не найден."))

    except Exception as e:
        await message.answer(_("❌ Не удалось удалить дашборд: {error}").format(error=str(e)))


@router.message(Command("list_dashboards"), StateFilter(None))
async def _list_dashboards_command(message: types.Message) -> None:
    """Показывает список всех активных дашбордов в этом чате"""
    try:
        async with async_session() as session:
            all_dashboards = await Dashboard.get_all_dashboards(session)

        # Фильтруем дашборды только для этого чата
        chat_dashboards = [d for d in all_dashboards if d.chat_id == message.chat.id]

        if not chat_dashboards:
            await message.answer(_("📭 В этом чате нет активных дашбордов."))
            return

        text = _("📊 <b>Активные дашборды:</b>\n\n")
        for dashboard in chat_dashboards:
            text += _("🔗 ID сообщения: <code>{message_id}</code>\n").format(
                message_id=dashboard.message_id
            )
            text += _("📅 Создан: {created}\n").format(
                created=dashboard.created_at.strftime("%Y-%m-%d %H:%M")
            )
            text += _("🔄 Обновлён: {updated}\n\n").format(
                updated=dashboard.updated_at.strftime("%Y-%m-%d %H:%M")
            )

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(_("❌ Не удалось получить список дашбордов: {error}").format(error=str(e)))
