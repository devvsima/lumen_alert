from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from loader import dp, tgbot, _

from data.config import DIR
from app.keyboards.inline.alert import alert_command_ikb
@dp.message_handler(CommandStart())
async def _start_command(message: types.Message):
    text = _(f"""👋Дароу, <a href='tg://user?id={message.from_user.id}'>{(message.from_user.full_name)}</a>
            
Это тг-бот Discord сервера <a href='https://discord.gg/5n29HHkn6R'>Lumen</a>.
Пока что сюда будут приходить уведомления с сервера. 👀""")
    
    with open(f'{DIR}/images/logo.jpg', "rb") as photo:
        await message.answer_photo(
            photo=photo,
            caption=(text),
            reply_markup=alert_command_ikb()
        )
