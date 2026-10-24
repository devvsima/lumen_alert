import discord
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from database.connect import async_session
from database.services.sources import DiscordSource
from dsbot.loader import dsbot
from tgbot.business.navigation import edit_navigation_message
from tgbot.keyboards.inline.source import (
    source_channels_ikb,
    source_guilds_ikb,
    source_search_cancel_ikb,
)
from tgbot.routers import user_router as router
from tgbot.loader import _
from tgbot.states import SourceSearchState
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


async def _render_guilds(
    message: types.Message, user_id: int, edit: bool = False
) -> None:
    await _sync_sources()
    async with async_session() as session:
        await DiscordSource.ensure_default_subscriptions(session, user_id)
        guilds = await DiscordSource.get_guilds(session)
        subscribed = await DiscordSource.get_user_guild_ids(session, user_id)
    if not guilds:
        await message.answer(_("❌ Discord-серверы пока недоступны."))
        return
    text = (
        _("🔔 <b>Источники уведомлений</b>\n\n")
        + _("Статус «Включено» — уведомления отправляются\n")
        + _("Статус «Выключено» — уведомления не отправляются\n\n")
        + _("Выберите Discord-сервер:")
    )
    markup = source_guilds_ikb(guilds, subscribed)
    if edit:
        await edit_navigation_message(
            message, text, reply_markup=markup, parse_mode="HTML"
        )
    else:
        await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("sources"), StateFilter(None))
async def sources_command(message: types.Message) -> None:
    try:
        await _render_guilds(message, message.from_user.id)
    except Exception:
        logger.exception("Failed to display notification sources")
        await message.answer(_("❌ Не удалось загрузить список источников."))


@router.callback_query(F.data == "source_settings")
async def source_settings_callback(callback: types.CallbackQuery) -> None:
    await _render_guilds(callback.message, callback.from_user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data == "source_back")
async def source_back_callback(callback: types.CallbackQuery) -> None:
    await callback.answer()
    await _render_guilds(callback.message, callback.from_user.id, edit=True)


@router.callback_query(F.data.startswith("source_guild_"))
async def source_guild_callback(callback: types.CallbackQuery) -> None:
    guild_id = int(callback.data.removeprefix("source_guild_"))
    async with async_session() as session:
        await DiscordSource.ensure_default_subscriptions(session, callback.from_user.id)
        channels = await DiscordSource.get_channels(session, guild_id)
        subscribed = await DiscordSource.get_user_channel_ids(session, callback.from_user.id)
    if not channels:
        await callback.answer(_("Для этого сервера нет голосовых каналов."), show_alert=True)
        return
    await edit_navigation_message(
        callback.message,
        _("🔔 <b>Выбор каналов</b>\n\nОтметьте каналы, откуда получать уведомления:"),
        reply_markup=source_channels_ikb(guild_id, channels, subscribed),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "source_noop")
async def source_noop_callback(callback: types.CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "source_search")
async def source_search_callback(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(SourceSearchState.waiting)
    await edit_navigation_message(
        callback.message,
        _("🔎 Введите название Discord-сервера для поиска:"),
        reply_markup=source_search_cancel_ikb(),
    )
    await callback.answer()


@router.callback_query(F.data == "source_search_cancel")
async def source_search_cancel_callback(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await state.clear()
    await _render_guilds(callback.message, callback.from_user.id, edit=True)
    await callback.answer()


@router.message(SourceSearchState.waiting)
async def source_search_message(message: types.Message, state: FSMContext) -> None:
    query = (message.text or "").strip().casefold()
    await state.clear()
    await _sync_sources()
    async with async_session() as session:
        await DiscordSource.ensure_default_subscriptions(session, message.from_user.id)
        guilds = [
            guild
            for guild in await DiscordSource.get_guilds(session)
            if query in (guild.name or "").casefold()
        ]
        subscribed = await DiscordSource.get_user_guild_ids(session, message.from_user.id)
    if not guilds:
        await message.answer(_("❌ Серверы по вашему запросу не найдены."))
        return
    await message.answer(
        _("🔎 Результаты поиска:"),
        reply_markup=source_guilds_ikb(guilds, subscribed),
    )


@router.callback_query(F.data.startswith("source_all_"))
async def source_all_callback(callback: types.CallbackQuery) -> None:
    prefix, action, guild_id, enabled = callback.data.split("_")
    async with async_session() as session:
        await DiscordSource.set_guild_subscriptions(
            session, callback.from_user.id, int(guild_id), enabled == "1"
        )
        channels = await DiscordSource.get_channels(session, int(guild_id))
        subscribed = await DiscordSource.get_user_channel_ids(session, callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=source_channels_ikb(int(guild_id), channels, subscribed)
    )
    await callback.answer(
        _("Все каналы включены.") if enabled == "1" else _("Все каналы отключены.")
    )


@router.callback_query(F.data.startswith("source_toggle_"))
async def source_toggle_callback(callback: types.CallbackQuery) -> None:
    prefix, action, guild_id, channel_id = callback.data.split("_")
    async with async_session() as session:
        enabled = await DiscordSource.toggle_channel(
            session, callback.from_user.id, int(guild_id), int(channel_id)
        )
        channels = await DiscordSource.get_channels(session, int(guild_id))
        subscribed = await DiscordSource.get_user_channel_ids(session, callback.from_user.id)
    await callback.message.edit_reply_markup(
        reply_markup=source_channels_ikb(int(guild_id), channels, subscribed)
    )
    await callback.answer(_("Канал добавлен.") if enabled else _("Канал отключён."))
