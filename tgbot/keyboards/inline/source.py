from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.loader import _


def _source_status(enabled: bool) -> str:
    return _("Включено") if enabled else _("Выключено")


def source_guilds_ikb(guilds, subscribed_guild_ids: set[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("🔎 Поиск сервера"),
            callback_data="source_search",
            style="primary",
        )
    )
    for guild in guilds:
        builder.row(
            InlineKeyboardButton(
                text=_("{name} — {status}").format(
                    name=guild.name,
                    status=_source_status(guild.id in subscribed_guild_ids),
                ),
                callback_data=f"source_guild_{guild.id}",
                style="success" if guild.id in subscribed_guild_ids else "danger",
            )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("ℹ️ Выберите сервер, затем каналы"),
            callback_data="source_noop",
            style="primary",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ Главное меню"),
            callback_data="menu_back",
            style="primary",
        )
    )
    return builder.as_markup()


def source_search_cancel_ikb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("⬅️ К серверам"),
                    callback_data="source_search_cancel",
                    style="primary",
                )
            ]
        ]
    )


def source_channels_ikb(guild_id: int, channels, subscribed_channel_ids: set[int]):
    builder = InlineKeyboardBuilder()
    all_selected = bool(channels) and all(
        channel.id in subscribed_channel_ids for channel in channels
    )
    builder.row(
        InlineKeyboardButton(
            text=_("Отключить все") if all_selected else _("Включить все"),
            callback_data=f"source_all_{guild_id}_{0 if all_selected else 1}",
            style="danger" if all_selected else "success",
        )
    )
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=_("{name} — {status}").format(
                    name=channel.name,
                    status=_source_status(channel.id in subscribed_channel_ids),
                ),
                callback_data=f"source_toggle_{guild_id}_{channel.id}",
                style="success"
                if channel.id in subscribed_channel_ids
                else "danger",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=_("⬅️ К серверам"),
            callback_data="source_back",
            style="primary",
        ),
    )
    return builder.as_markup()
