from aiogram import types
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter

from data.config import DISCORD_CHANNEL_URL, LOGO_DIR
from tgbot.keyboards.inline.alert import alert_command_ikb
from tgbot.routers import start_router
from tgbot.text import message_text as mt


@start_router.message(CommandStart(), StateFilter(None))
async def _start_command(message: types.Message) -> None:
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
