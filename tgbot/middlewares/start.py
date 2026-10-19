from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database.models.telegram_user import TgUserStatus
from database.services.tg_users import TgUser
from utils.base62 import decode_base62


class StartMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, message: Message, data: dict) -> Any:
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

        if is_create and data["command"].args:
            argument = data["command"].args
            if not argument.startswith("guild_"):
                inviter_id = decode_base62(argument)
                inviter = await TgUser.get_by_id(session, inviter_id)
                if inviter is not None:
                    await TgUser.increment_referral_count(session, inviter)

        return await handler(message, data)
