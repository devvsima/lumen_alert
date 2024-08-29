from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from loader import dp, tgbot
from app.filters.admin import Admin

from database.service.stats import get_users_stats

@dp.message_handler(Admin(), Command("admin"))
async def _admin_command(message: types.Message):
    await message.answer(
        text=f"К огромному сожалению ты админ😩\n🫂Users: {get_users_stats()}\n\n/send - для рассылки"
    )
