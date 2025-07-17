from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.logging import logger

from ..models.user import TgUserModel


class TgUser:
    @staticmethod
    async def get(session: AsyncSession, user_id: int) -> TgUserModel | None:
        """Возвращает пользователя по его id"""
        return await session.get(TgUserModel, user_id)

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
        if user := await TgUser.get(session, user_id):
            return user, False
        await TgUser.create(session, user_id=user_id, username=username, language=language)
        user = await TgUser.get(session, user_id)
        return user, True

    @staticmethod
    async def create(
        session: AsyncSession, user_id: int, username: str = None, language: str = None
    ) -> TgUserModel:
        """Создает нового пользователя"""
        logger.log("DATABASE", f"New user: {user_id} (@{username}) {language}")
        session.add(TgUserModel(id=user_id, username=username, language=language))
        await session.commit()

    @staticmethod
    async def update_username(
        session: AsyncSession, user: TgUserModel, username: str = None
    ) -> None:
        """Обновляет данные пользователя"""
        user.username = username
        await session.commit()
        logger.log("DATABASE", f"{user.id} ({user.username}): обновленно имя на - {username}")

    @staticmethod
    async def increment_referral_count(
        session: AsyncSession, user: TgUserModel, num: int = 1
    ) -> None:
        """Добавляет приведенного реферала к пользователю {inviter_id}"""
        user.referral += num
        await session.commit()
        logger.log("DATABASE", f"{user.id} (@{user.username}): привел нового пользователя")

    @staticmethod
    async def update_language(session: AsyncSession, user: TgUserModel, language: str) -> None:
        """Изменяет язык пользователя на {language}"""
        user.language = language
        await session.commit()
        logger.log("DATABASE", f"{user.id} (@{user.username}): изменил язык на - {language}")

    @staticmethod
    async def update_isbanned(session: AsyncSession, user: TgUserModel, is_banned: bool) -> None:
        """Меняет статус блокировки пользователя на {is_banned}"""
        user.is_banned = is_banned
        await session.commit()
        logger.log(
            "DATABASE", f"{user.id} (@{user.username}): статус блокировки изменен на - {is_banned}"
        )
