from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.services.base import BaseService

from ..models import GroupMemberModel, GroupModel, UserModel


class Group(BaseService):
    model = GroupModel


class GroupMember(BaseService):
    model = GroupMemberModel

    @staticmethod
    async def add_user(session: AsyncSession, user_id: int, group_id: int):
        # Проверяем, есть ли уже такой пользователь в группе
        result = await session.execute(
            select(GroupMemberModel).filter_by(user_id=user_id, group_id=group_id)
        )
        existing_record = result.scalars().first()

        if not existing_record:
            # Если записи нет — добавляем
            new_member = GroupMemberModel(user_id=user_id, group_id=group_id)
            session.add(new_member)
            await session.commit()

    @staticmethod
    async def get_members_username(session: AsyncSession, group_id: int):
        result = await session.execute(
            select(UserModel.username)
            .join(GroupMemberModel, GroupMemberModel.user_id == UserModel.id)
            .filter(GroupMemberModel.group_id == group_id)
        )
        return result.scalars().all()

    @staticmethod
    async def is_user_in_group(session, user_id: int, group_id: int) -> bool:
        result = await session.execute(
            select(GroupMemberModel).where(
                GroupMemberModel.user_id == user_id, GroupMemberModel.group_id == group_id
            )
        )
        return result.scalar() is not None
