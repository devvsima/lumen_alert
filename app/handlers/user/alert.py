from aiogram import types
from aiogram.dispatcher.filters import Text, Command

from loader import dp, tgbot, _
    
from database.service.users import get_notification_enabled_users
from database.service.users import toggle_alert
from database.models.users import Users

from app.keyboards.inline.alert import alert_off_ikb, alert_on_ikb, ds_link_ikb

async def send_telegram_message(text):
    for i in get_notification_enabled_users():
        try:
            from utils.logging import logger
            await tgbot.send_message(chat_id=i, text=text, reply_markup=ds_link_ikb())
            logger.info(f"{i} | {text}")
        except Exception as e:
            logger.error(f"! {i} | {text}")
            
            pass
# @dp.message_handler(Command('alert'))


@dp.callback_query_handler(Text("alert_settings"))
async def _alert_settings(callback: types.CallbackQuery, user: Users):
    if user.alert == True:
        await callback.message.answer("У тебя включены уведомления 🌞\n\nМожешь выключить нажав кнопку ниже.", reply_markup=alert_off_ikb())
    elif user.alert == False:
        await callback.message.answer("У тебя уведомления выключены 🌚\n\nМожешь включить нажав кнопку ниже.", reply_markup=alert_on_ikb())
        

@dp.callback_query_handler(Text("alert_off"))
@dp.callback_query_handler(Text("alert_on"))
async def _alert_off_or_on(callback: types.CallbackQuery, user: Users):
    # toggle_alert(callback.from_user.id)
    await _alert_settings(callback, user)