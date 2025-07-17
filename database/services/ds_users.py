from sqlalchemy.ext.asyncio import AsyncSession

from database.services.base import BaseService

from ..models.discord_user import DsUserModel


class DsUser(BaseService):
    model = DsUserModel

    @staticmethod
    async def get_or_create(
        session: AsyncSession, user_id: int, display_name: str = None, name: str = None
    ) -> DsUserModel:
        if user := await DsUser.get_by_id(session, user_id):
            return user, False
        await DsUser.create(session=session, id=user_id, display_name=display_name, name=name)
        user = await DsUser.get_by_id(session, user_id)
        return user, True
