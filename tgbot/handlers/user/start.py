from aiogram import types
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter

from data.config import DISCORD_CHANNEL_URL, LOGO_DIR
from database.connect import async_session
from database.services.sources import DiscordSource
from tgbot.keyboards.inline.alert import alert_command_ikb
from tgbot.loader import _
from tgbot.routers import start_router
from tgbot.text import message_text as mt


@start_router.message(CommandStart(), StateFilter(None))
async def _start_command(message: types.Message, is_new_user: bool = False) -> None:
    argument = (message.text or "").split(maxsplit=1)
    is_guild_link = len(argument) == 2 and argument[1].startswith("guild_")
    if is_guild_link:
        try:
            guild_id = int(argument[1].removeprefix("guild_"))
        except ValueError:
            guild_id = None
        if guild_id is not None:
            async with async_session() as session:
                added = await DiscordSource.subscribe_guild_if_missing(
                    session, message.from_user.id, guild_id
                )
            await message.answer(
                _("✅ Сервер добавлен в уведомления.")
                if added is True
                else (
                    _("❌ Сервер не найден или пока не содержит доступных каналов.")
                    if added is None
                    else _("ℹ️ Уведомления для этого сервера уже включены.")
                )
            )
        else:
            await message.answer(_("❌ Некорректная ссылка на Discord-сервер."))

    if is_new_user:
        photo = types.FSInputFile(LOGO_DIR)
        text = mt.WELCOME.format(
            user_id=message.from_user.id,
            name=message.from_user.full_name,
            url=DISCORD_CHANNEL_URL,
        )
        await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=alert_command_ikb(),
        )
        return

    await message.answer(
        _("🏠 <b>Главное меню</b>\nВыберите нужный раздел:"),
        reply_markup=alert_command_ikb(),
        parse_mode="HTML",
    )
