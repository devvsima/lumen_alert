from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.loader import _

def source_guilds_ikb(guilds, subscribed_guild_ids: set[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("🔎 Поиск сервера"),
            callback_data="source_search",
        )
    )
    for guild in guilds:
        builder.row(
            InlineKeyboardButton(
                text=f"{'🟢' if guild.id in subscribed_guild_ids else '🔴'} {guild.name}",
                callback_data=f"source_guild_{guild.id}",
            )
    )
    builder.row(
    InlineKeyboardButton(
        text=_("ℹ️ Выберите сервер, затем каналы"),
        callback_data="source_noop",
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
            text=_("🔴 Отключить все") if all_selected else _("🟢 Включить все"),
            callback_data=f"source_all_{guild_id}_{0 if all_selected else 1}",
        )
    )
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"{'🟢' if channel.id in subscribed_channel_ids else '🔴'} {channel.name}",
                callback_data=f"source_toggle_{guild_id}_{channel.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text=_("⬅️ К серверам"), callback_data="source_back"),
    )
    return builder.as_markup()
