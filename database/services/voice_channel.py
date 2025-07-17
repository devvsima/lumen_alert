from typing import List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.services.base import BaseService
from ..models.voice_channel import VoiceChannelUserModel


class VoiceChannelUser(BaseService):
    model = VoiceChannelUserModel

    @staticmethod
    async def add_user_to_channel(
        session: AsyncSession,
        user_id: int,
        user_name: str,
        display_name: str,
        channel_id: int,
        channel_name: str
    ) -> VoiceChannelUserModel:
        """Добавить пользователя в голосовой канал"""
        # Сначала удаляем пользователя из всех каналов (если он был)
        await VoiceChannelUser.remove_user_from_all_channels(session, user_id)
        
        # Добавляем в новый канал
        user_in_channel = await VoiceChannelUser.create(
            session=session,
            user_id=user_id,
            user_name=user_name,
            display_name=display_name,
            channel_id=channel_id,
            channel_name=channel_name
        )
        await session.commit()
        return user_in_channel

    @staticmethod
    async def remove_user_from_all_channels(session: AsyncSession, user_id: int) -> None:
        """Удалить пользователя из всех голосовых каналов"""
        await session.execute(
            delete(VoiceChannelUserModel).where(VoiceChannelUserModel.user_id == user_id)
        )
        await session.commit()

    @staticmethod
    async def get_all_users_in_channels(session: AsyncSession) -> List[VoiceChannelUserModel]:
        """Получить всех пользователей в голосовых каналах"""
        result = await session.execute(
            select(VoiceChannelUserModel).order_by(
                VoiceChannelUserModel.channel_name,
                VoiceChannelUserModel.display_name
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_users_by_channel(session: AsyncSession, channel_id: int) -> List[VoiceChannelUserModel]:
        """Получить пользователей в конкретном канале"""
        result = await session.execute(
            select(VoiceChannelUserModel)
            .where(VoiceChannelUserModel.channel_id == channel_id)
            .order_by(VoiceChannelUserModel.display_name)
        )
        return result.scalars().all()
