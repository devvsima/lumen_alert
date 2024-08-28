from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text

from loader import dp


@dp.message_handler(Text("💤"), state="*")
@dp.message_handler(Command("cancel"), state="*")
async def _cancel_command(message: types.Message, state: FSMContext):
    if state is None:        
        return
    await state.finish()
