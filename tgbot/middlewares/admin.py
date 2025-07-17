from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from data.config import telegram_bot
from database.services.users import TgUser


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, message: Message, data: dict) -> Any:
        session = data["session"]
        if user := await TgUser.get(session, message.from_user.id):
            if user.id in telegram_bot.ADMINS:
                data["user"] = user
                return await handler(message, data)
        return
