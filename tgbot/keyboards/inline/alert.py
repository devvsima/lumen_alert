from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from data.config import DISCORD_CHANNEL_URL
from tgbot.loader import _


def alert_command_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Notifications 🔔"), callback_data="alert_settings"),
            ],
        ],
    )
    return ikb


def ds_link_ikb():
    ikb = InlineKeyboardMarkup(
        resize_keyboard=True,
        inline_keyboard=[
            [
                InlineKeyboardButton(text=_("Join the Discord channel"), url=DISCORD_CHANNEL_URL),
            ],
        ],
    )
    return ikb


def alert_off_on_ikb(is_alert: bool):
    ikb = InlineKeyboardMarkup()
    if is_alert:
        ikb.add(InlineKeyboardButton(text=_("Turn off 🔕"), callback_data="alert_off"))
    else:
        ikb.add(InlineKeyboardButton(text=_("Turn on 🔔"), callback_data="alert_on"))
    return ikb
