from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.connect import async_session
from database.services.dashboard import Dashboard
from tgbot.routers import user_router as router


@router.message(Command("remove_dashboard"), StateFilter(None))
async def _remove_dashboard_command(message: types.Message) -> None:
    """Удаляет дашборд по reply на сообщение с дашбордом"""
    if not message.reply_to_message:
        await message.answer("❌ Please reply to a dashboard message to remove it")
        return
    
    try:
        async with async_session() as session:
            success = await Dashboard.delete_dashboard(
                session, 
                message.chat.id, 
                message.reply_to_message.message_id
            )
            
        if success:
            await message.answer("✅ Dashboard removed successfully!")
            # Удаляем само сообщение с дашбордом
            try:
                await message.reply_to_message.delete()
            except Exception:
                pass  # Игнорируем ошибки удаления
        else:
            await message.answer("❌ Dashboard not found")
            
    except Exception as e:
        await message.answer(f"❌ Error removing dashboard: {str(e)}")


@router.message(Command("list_dashboards"), StateFilter(None))
async def _list_dashboards_command(message: types.Message) -> None:
    """Показывает список всех активных дашбордов в этом чате"""
    try:
        async with async_session() as session:
            all_dashboards = await Dashboard.get_all_dashboards(session)
            
        # Фильтруем дашборды только для этого чата
        chat_dashboards = [d for d in all_dashboards if d.chat_id == message.chat.id]
        
        if not chat_dashboards:
            await message.answer("📭 No active dashboards in this chat")
            return
            
        text = "📊 **Active Dashboards:**\n\n"
        for dashboard in chat_dashboards:
            text += f"🔗 Message ID: `{dashboard.message_id}`\n"
            text += f"📅 Created: {dashboard.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            text += f"🔄 Updated: {dashboard.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer(f"❌ Error listing dashboards: {str(e)}")
