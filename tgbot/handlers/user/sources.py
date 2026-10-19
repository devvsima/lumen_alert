import discord
from aiogram import F, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.connect import async_session
from database.services.sources import DiscordSource
from dsbot.loader import dsbot
from tgbot.keyboards.inline.source import source_channels_ikb, source_guilds_ikb
from tgbot.routers import user_router as router
from utils.logging import logger


async def _sync_sources() -> None:
    if not dsbot.is_ready():
        return
    async with async_session() as session:
        for guild in dsbot.guilds:
            channels = [
                channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)
            ]
            await DiscordSource.sync_guild(session, guild.id, guild.name, channels)


async def _render_guilds(message: types.Message, user_id: int) -> None:
    await _sync_sources()
    async with async_session() as session:
        guilds = await DiscordSource.get_guilds(session)
        subscribed = await DiscordSource.get_user_guild_ids(session, user_id)
    if not guilds:
        await message.answer("❌ Discord-серверы пока недоступны.")
        return
    await message.answer(
        "🔔 <b>Источники уведомлений</b>\n\nВыберите Discord-сервер:",
        reply_markup=source_guilds_ikb(guilds, subscribed),
        parse_mode="HTML",
    )


@router.message(Command("sources"), StateFilter(None))
async def sources_command(message: types.Message) -> None:
    try:
        await _render_guilds(message, message.from_user.id)
    except Exception:
        logger.exception("Failed to display notification sources")
        await message.answer("❌ Не удалось загрузить список источников.")


@router.callback_query(F.data == "source_settings")
async def source_settings_callback(callback: types.CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await _render_guilds(callback.message, callback.from_user.id)


@router.callback_query(F.data == "source_back")
async def source_back_callback(callback: types.CallbackQuery) -> None:
    await callback.answer()
    await _render_guilds(callback.message, callback.from_user.id)


@router.callback_query(F.data.startswith("source_guild_"))
async def source_guild_callback(callback: types.CallbackQuery) -> None:
    guild_id = int(callback.data.removeprefix("source_guild_"))
    async with async_session() as session:
        channels = await DiscordSource.get_channels(session, guild_id)
        subscribed = await DiscordSource.get_user_channel_ids(session, callback.from_user.id)
    if not channels:
        await callback.answer("Для этого сервера нет голосовых каналов.", show_alert=True)
        return
    await callback.message.edit_text(
        "🔔 <b>Выбор каналов</b>\n\nОтметьте каналы, откуда получать уведомления:",
        reply_markup=source_channels_ikb(guild_id, channels, subscribed),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("source_toggle_"))
async def source_toggle_callback(callback: types.CallbackQuery) -> None:
    _, _, guild_id, channel_id = callback.data.split("_")
    async with async_session() as session:
        enabled = await DiscordSource.toggle_channel(
            session, callback.from_user.id, int(guild_id), int(channel_id)
        )
        channels = await DiscordSource.get_channels(session, int(guild_id))
        subscribed = await DiscordSource.get_user_channel_ids(session, callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=source_channels_ikb(int(guild_id), channels, subscribed)
    )
    await callback.answer("Канал добавлен." if enabled else "Канал отключён.")
