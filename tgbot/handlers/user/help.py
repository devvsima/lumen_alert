from aiogram import types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from tgbot.routers import user_router as router
from tgbot.text import message_text as mt


@router.message(Command("help"), StateFilter(None))
async def _help_command(message: types.Message) -> None:
    """Дает описание бота"""
    await message.answer(mt.INFO)
