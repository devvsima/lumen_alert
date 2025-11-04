from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.config import DISCORD_CHANNEL_URL
from tgbot.loader import _


def alert_command_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Notifications 🔔"), callback_data="alert_settings"),
            ],
        ],
    )
    return ikb


def ds_link_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Join the Discord channel"), url=DISCORD_CHANNEL_URL),
            ],
        ],
    )
    return ikb


def dashboard_ikb(online_count: str):
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_(f"Online: {online_count}"), url=DISCORD_CHANNEL_URL),
            ],
        ],
    )
    return ikb


def alert_settings_ikb(user) -> InlineKeyboardMarkup:
    """Клавиатура для настройки уведомлений"""
    builder = InlineKeyboardBuilder()

    # Настройки уведомлений с проверкой на существование атрибутов
    alert_on_join = getattr(user, "alert_on_join", True)
    alert_on_leave = getattr(user, "alert_on_leave", False)
    alert_on_switch = getattr(user, "alert_on_switch", False)

    builder.row(
        InlineKeyboardButton(
            text=f"📥 Присоединение: {'✅' if alert_on_join else '❌'}",
            callback_data=f"toggle_join_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"📤 Покидание: {'✅' if alert_on_leave else '❌'}",
            callback_data=f"toggle_leave_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🔄 Переключение: {'✅' if alert_on_switch else '❌'}",
            callback_data=f"toggle_switch_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🔔 Все уведомления: {'✅' if user.is_alert else '❌'}",
            callback_data=f"toggle_all_{user.id}",
        )
    )
    # builder.row(
    #     InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_settings_{user.id}")
    # )

    return builder.as_markup()


def alert_off_on_ikb(is_alert: bool):
    ikb = InlineKeyboardMarkup()
    if is_alert:
        ikb.add(InlineKeyboardButton(text=_("Turn off 🔕"), callback_data="alert_off"))
    else:
        ikb.add(InlineKeyboardButton(text=_("Turn on 🔔"), callback_data="alert_on"))
    return ikb


def alert_settings_ikb(user) -> InlineKeyboardMarkup:
    """Клавиатура для настройки уведомлений"""
    builder = InlineKeyboardBuilder()

    # Настройки уведомлений
    builder.row(
        InlineKeyboardButton(
            text=f"📥 Присоединение: {'✅' if user.alert_on_join else '❌'}",
            callback_data=f"toggle_join_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"📤 Покидание: {'✅' if user.alert_on_leave else '❌'}",
            callback_data=f"toggle_leave_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🔄 Переключение: {'✅' if user.alert_on_switch else '❌'}",
            callback_data=f"toggle_switch_{user.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🔔 Все уведомления: {'✅' if user.is_alert else '❌'}",
            callback_data=f"toggle_all_{user.id}",
        )
    )
    # builder.row(
    #     InlineKeyboardButton(text="🔄 Обновить", callback_data=f"refresh_settings_{user.id}")
    # )

    return builder.as_markup()
