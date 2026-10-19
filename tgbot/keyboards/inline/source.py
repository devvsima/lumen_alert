from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def source_guilds_ikb(guilds, subscribed_guild_ids: set[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for guild in guilds:
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if guild.id in subscribed_guild_ids else '⬜'} {guild.name}",
                callback_data=f"source_guild_{guild.id}",
            )
        )
    return builder.as_markup()


def source_channels_ikb(guild_id: int, channels, subscribed_channel_ids: set[int]):
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if channel.id in subscribed_channel_ids else '⬜'} {channel.name}",
                callback_data=f"source_toggle_{guild_id}_{channel.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ К серверам", callback_data="source_back")
    )
    return builder.as_markup()
