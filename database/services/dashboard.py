from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.services.base import BaseService

from ..models.dashboard import DashboardModel


class Dashboard(BaseService):
    model = DashboardModel

    @staticmethod
    async def create_dashboard(
        session: AsyncSession,
        chat_id: int,
        message_id: int
    ) -> DashboardModel:
        """Создать новый дашборд"""
        dashboard = await Dashboard.create(
            session=session,
            chat_id=chat_id,
            message_id=message_id
        )
        await session.commit()
        return dashboard

    @staticmethod
    async def get_by_chat_id(session: AsyncSession, chat_id: int) -> DashboardModel | None:
        result = await session.execute(
            select(DashboardModel).where(DashboardModel.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def replace_dashboard(
        session: AsyncSession, chat_id: int, message_id: int
    ) -> DashboardModel | None:
        previous = await Dashboard.get_by_chat_id(session, chat_id)
        if previous is not None:
            await session.delete(previous)
            await session.flush()
        next_id = await session.scalar(
            select(func.coalesce(func.max(DashboardModel.id), 0) + 1)
        )
        dashboard = DashboardModel(
            id=next_id,
            chat_id=chat_id,
            message_id=message_id,
        )
        session.add(dashboard)
        await session.commit()
        return previous

    @staticmethod
    async def get_all_dashboards(session: AsyncSession) -> List[DashboardModel]:
        """Получить все дашборды"""
        result = await session.execute(select(DashboardModel))
        return result.scalars().all()

    @staticmethod
    async def delete_dashboard(session: AsyncSession, chat_id: int, message_id: int) -> bool:
        """Удалить дашборд"""
        dashboard = await session.execute(
            select(DashboardModel).where(
                DashboardModel.chat_id == chat_id,
                DashboardModel.message_id == message_id
            )
        )
        dashboard = dashboard.scalar_one_or_none()

        if dashboard:
            await session.delete(dashboard)
            await session.commit()
            return True
        return False
