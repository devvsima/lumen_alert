from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from database.models.tg_user import TgUserStatus
from database.services import TgUser


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable, message: Message | CallbackQuery, data: dict
    ) -> Any:
        session = data["session"]
        user, is_create = await TgUser.get_or_create(
            session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            language=message.from_user.language_code,
        )
        if user.status == TgUserStatus.Banned:
            return

        data["user"] = user
        return await handler(message, data)
