from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from database.services import Group, GroupMember, User


class GroupMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable, message: Message | CallbackQuery, data: dict
    ) -> Any:
        session = data["session"]
        user, is_create = await User.get_or_create(
            session=session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language=message.from_user.language_code,
        )
        if not user.is_banned:
            try:
                if message.chat.title:
                    await Group.create(
                        session=session,
                        id=message.chat.id,
                        title=message.chat.title,
                        group_type=message.chat.type,
                    )
                    await GroupMember.add_user(session, message.from_user.id, message.chat.id)
            except:
                ...
            data["user"] = user
            return await handler(message, data)
        return
