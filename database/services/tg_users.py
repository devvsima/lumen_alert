from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.services.base import BaseService
from utils.logging import logger

from ..models.telegram_user import TgUserModel, TgUserStatus


class TgUser(BaseService):
    model = TgUserModel

    @staticmethod
    async def get_alert_user_ids(session: AsyncSession) -> list[int]:
        try:
            logger.log("DATABASE", "Executing query to get alert user IDs...")
            result = await session.execute(
                select(TgUserModel.id).where(TgUserModel.is_alert.is_(True))
            )
            user_ids = [row[0] for row in result.fetchall()]
            logger.log("DATABASE", f"Found {len(user_ids)} users with alerts enabled")
            return user_ids
        except Exception as e:
            logger.error(f"Error in get_alert_user_ids: {e}")
            return []

    @staticmethod
    async def get_or_create(
        session: AsyncSession, user_id: int, username: str = None, language: str = None
    ) -> TgUserModel:
        if user := await TgUser.get_by_id(session, user_id):
            return user, False
        await TgUser.create(session, user_id=user_id, username=username, language=language)
        user = await TgUser.get_by_id(session, user_id)
        return user, True

    @staticmethod
    async def increment_referral_count(
        session: AsyncSession, user: TgUserModel, num: int = 1
    ) -> None:
        """Добавляет приведенного реферала к пользователю {inviter_id}"""
        user.referral += num
        await session.commit()
        logger.log("DATABASE", f"{user.id} (@{user.username}): привел нового пользователя")

    @staticmethod
    async def get_users_for_join_alerts(session: AsyncSession) -> list[int]:
        """Получает список ID пользователей, которые хотят получать уведомления о присоединении к каналам"""
        result = await session.execute(
            select(TgUserModel.id).where(
                and_(
                    TgUserModel.is_alert.is_(True),
                    TgUserModel.alert_on_join.is_(True),
                    TgUserModel.status >= TgUserStatus.TgUser,
                )
            )
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def get_users_for_leave_alerts(session: AsyncSession) -> list[int]:
        """Получает список ID пользователей, которые хотят получать уведомления о покидании каналов"""
        result = await session.execute(
            select(TgUserModel.id).where(
                and_(
                    TgUserModel.is_alert.is_(True),
                    TgUserModel.alert_on_leave.is_(True),
                    TgUserModel.status >= TgUserStatus.TgUser,
                )
            )
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def get_users_for_switch_alerts(session: AsyncSession) -> list[int]:
        """Получает список ID пользователей, которые хотят получать уведомления о переключении каналов"""
        result = await session.execute(
            select(TgUserModel.id).where(
                and_(
                    TgUserModel.is_alert.is_(True),
                    TgUserModel.alert_on_switch.is_(True),
                    TgUserModel.status >= TgUserStatus.TgUser,
                )
            )
        )
        return [row[0] for row in result.fetchall()]

    @staticmethod
    async def update_alert_settings(
        session: AsyncSession,
        user_id: int,
        alert_on_join: bool = None,
        alert_on_leave: bool = None,
        alert_on_switch: bool = None,
    ) -> bool:
        """Обновляет настройки уведомлений пользователя"""
        try:
            # Сначала попробуем обновить через ORM
            user = await TgUser.get_by_id(session, user_id)
            if not user:
                return False
            
            # Обновляем только те поля, которые переданы
            if alert_on_join is not None:
                if hasattr(user, 'alert_on_join'):
                    user.alert_on_join = alert_on_join
                else:
                    # Если поле не существует, можно добавить его динамически
                    setattr(user, 'alert_on_join', alert_on_join)
                    
            if alert_on_leave is not None:
                if hasattr(user, 'alert_on_leave'):
                    user.alert_on_leave = alert_on_leave
                else:
                    setattr(user, 'alert_on_leave', alert_on_leave)
                    
            if alert_on_switch is not None:
                if hasattr(user, 'alert_on_switch'):
                    user.alert_on_switch = alert_on_switch
                else:
                    setattr(user, 'alert_on_switch', alert_on_switch)
            
            await session.commit()
            await session.refresh(user)  # Обновляем объект из БД
            return True
            
        except Exception as e:
            logger.error(f"Error updating alert settings: {e}")
            await session.rollback()
            return False
