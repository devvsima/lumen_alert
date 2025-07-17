from aiogram import types
from aiogram.filters import CommandStart
from aiogram.filters.state import StateFilter

from tgbot.routers import start_router
from tgbot.text import message_text as mt


@start_router.message(CommandStart(), StateFilter(None))
async def _start_command(message: types.Message) -> None:
    await message.answer(mt.WELCOME.format(message.from_user.id, message.from_user.full_name))
