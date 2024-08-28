from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from loader import dp, tgbot
from app.filters.admin import Admin
from app.states.send import Send

from ..user.alert import send_telegram_message

@dp.message_handler(Admin(), Command("send"))
async def _admin_command(message: types.Message):
    await message.answer(
        text=f"Напишите сообщение, которое вы хотите отправить всем пользователям. 🥸\n\n/cancel чтобы выйти"
    )
    await Send.input.set()

@dp.message_handler(content_types=ContentType.TEXT, state=Send.input)
async def _send(message: types.Message, state: FSMContext):
    await Send.next()
    text = f"<a href='tg://user?id={message.from_user.id}'>{(message.from_user.full_name)}</a> сообщает ееебически важную инфу:\n\n<code>{message.text}</code>"
    await send_telegram_message(text)