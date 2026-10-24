from aiogram import F, types
from aiogram.filters.state import StateFilter

from tgbot.business.voice_update_dashboard import create_new_dashboard
from tgbot.business.navigation import edit_navigation_message
from tgbot.keyboards.inline.alert import alert_command_ikb, menu_back_ikb
from tgbot.keyboards.inline.lang import lang_ikb
from tgbot.loader import _
from tgbot.routers import user_router as router
from tgbot.text import message_text as mt
from tgbot.loader import bot
from utils.base62 import encode_base62


@router.callback_query(F.data == "menu_back", StateFilter(None))
async def menu_back_callback(callback: types.CallbackQuery) -> None:
    await edit_navigation_message(
        callback.message,
        _("🏠 <b>Главное меню</b>\nВыберите нужный раздел:"),
        reply_markup=alert_command_ikb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "menu_language", StateFilter(None))
async def menu_language_callback(callback: types.CallbackQuery) -> None:
    await edit_navigation_message(
        callback.message,
        mt.CHANGE_LANG,
        reply_markup=lang_ikb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_help", StateFilter(None))
async def menu_help_callback(callback: types.CallbackQuery) -> None:
    await edit_navigation_message(
        callback.message,
        _(
            "❓ <b>Помощь</b>\n\n"
            "🎯 В разделе «Серверы и каналы» выберите сервер и каналы "
            "для уведомлений.\n"
            "🔔 В разделе «Уведомления» настройте типы событий.\n"
            "📊 Кнопка «Дашборд» создаёт или обновляет дашборд текущего чата."
        ),
        reply_markup=menu_back_ikb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "menu_invite", StateFilter(None))
async def menu_invite_callback(callback: types.CallbackQuery, user) -> None:
    bot_user = await bot.get_me()
    await edit_navigation_message(
        callback.message,
        mt.INVITE_FRIENDS.format(
            user.referral,
            bot_user.username,
            encode_base62(callback.from_user.id),
        ),
        reply_markup=menu_back_ikb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_dashboard", StateFilter(None))
async def menu_dashboard_callback(callback: types.CallbackQuery) -> None:
    dashboard_message_id = await create_new_dashboard(callback.message.chat.id)
    await edit_navigation_message(
        callback.message,
        _("✅ Дашборд создан или обновлён. ID сообщения: {message_id}").format(
            message_id=dashboard_message_id
        ),
        reply_markup=menu_back_ikb(),
    )
    await callback.answer()
