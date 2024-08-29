from aiogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from loader import _

def alert_command_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Уведоления 🔔", callback_data='alert_settings'),
            ],
        ],
    )
    return ikb

def ds_link_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Присоединиться к Discord канал", url="https://discord.gg/5n29HHkn6R"),
            ],
        ],
    )
    return ikb

def alert_off_on_ikb(is_alert: bool):
    ikb = InlineKeyboardMarkup()
    if is_alert:
        ikb.add(InlineKeyboardButton(text="Выключить 🔕", callback_data='alert_off'))
    else:
        ikb.add(InlineKeyboardButton(text="Включить 🔔", callback_data='alert_on'))
    return ikb
    
    
        