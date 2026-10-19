from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.guild import GuildModel
from database.models.source import DiscordChannelModel, TelegramSourceSubscriptionModel
from database.models.telegram_user import TgUserModel, TgUserStatus


class DiscordSource:
    @staticmethod
    async def sync_guild(session: AsyncSession, guild_id: int, guild_name: str, channels) -> None:
        guild = await session.get(GuildModel, guild_id)
        if guild is None:
            guild = GuildModel(id=guild_id, name=guild_name)
            session.add(guild)
        else:
            guild.name = guild_name

        for channel in channels:
            if channel is None:
                continue
            db_channel = await session.get(DiscordChannelModel, channel.id)
            if db_channel is None:
                session.add(
                    DiscordChannelModel(id=channel.id, guild_id=guild_id, name=channel.name)
                )
            else:
                db_channel.guild_id = guild_id
                db_channel.name = channel.name
        await session.commit()

    @staticmethod
    async def get_guilds(session: AsyncSession) -> list[GuildModel]:
        result = await session.execute(select(GuildModel).order_by(GuildModel.name))
        return list(result.scalars().all())

    @staticmethod
    async def get_channels(session: AsyncSession, guild_id: int) -> list[DiscordChannelModel]:
        result = await session.execute(
            select(DiscordChannelModel)
            .where(
                DiscordChannelModel.guild_id == guild_id,
                DiscordChannelModel.is_enabled.is_(True),
            )
            .order_by(DiscordChannelModel.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all_channels(
        session: AsyncSession, guild_id: int
    ) -> list[DiscordChannelModel]:
        result = await session.execute(
            select(DiscordChannelModel)
            .where(DiscordChannelModel.guild_id == guild_id)
            .order_by(DiscordChannelModel.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def toggle_channel_access(
        session: AsyncSession, guild_id: int, channel_id: int
    ) -> bool | None:
        channel = await session.get(DiscordChannelModel, channel_id)
        if channel is None or channel.guild_id != guild_id:
            return None
        channel.is_enabled = not channel.is_enabled
        await session.commit()
        return channel.is_enabled

    @staticmethod
    async def get_user_channel_ids(session: AsyncSession, user_id: int) -> set[int]:
        result = await session.execute(
            select(TelegramSourceSubscriptionModel.channel_id).where(
                TelegramSourceSubscriptionModel.user_id == user_id
            )
        )
        return set(result.scalars().all())

    @staticmethod
    async def get_user_guild_ids(session: AsyncSession, user_id: int) -> set[int]:
        result = await session.execute(
            select(TelegramSourceSubscriptionModel.guild_id)
            .where(TelegramSourceSubscriptionModel.user_id == user_id)
            .distinct()
        )
        return set(result.scalars().all())

    @staticmethod
    async def toggle_channel(
        session: AsyncSession, user_id: int, guild_id: int, channel_id: int
    ) -> bool:
        query = select(TelegramSourceSubscriptionModel).where(
            TelegramSourceSubscriptionModel.user_id == user_id,
            TelegramSourceSubscriptionModel.guild_id == guild_id,
            TelegramSourceSubscriptionModel.channel_id == channel_id,
        )
        subscription = (await session.execute(query)).scalar_one_or_none()
        if subscription is None:
            session.add(
                TelegramSourceSubscriptionModel(
                    user_id=user_id, guild_id=guild_id, channel_id=channel_id
                )
            )
            enabled = True
        else:
            await session.delete(subscription)
            enabled = False
        await session.commit()
        return enabled

    @staticmethod
    async def get_recipient_ids(
        session: AsyncSession,
        guild_id: int,
        channel_ids: set[int],
        alert_field: str | None = None,
    ) -> list[int]:
        if not channel_ids:
            return []
        conditions = [
            TgUserModel.is_alert.is_(True),
            TgUserModel.status >= TgUserStatus.TgUser,
            TelegramSourceSubscriptionModel.guild_id == guild_id,
            TelegramSourceSubscriptionModel.channel_id.in_(channel_ids),
            DiscordChannelModel.guild_id == guild_id,
            DiscordChannelModel.is_enabled.is_(True),
        ]
        if alert_field is not None:
            if alert_field not in {"alert_on_join", "alert_on_leave", "alert_on_switch"}:
                raise ValueError(f"Unsupported alert field: {alert_field}")
            conditions.append(getattr(TgUserModel, alert_field).is_(True))
        result = await session.execute(
            select(TelegramSourceSubscriptionModel.user_id)
            .join(TgUserModel, TgUserModel.id == TelegramSourceSubscriptionModel.user_id)
            .join(
                DiscordChannelModel,
                DiscordChannelModel.id == TelegramSourceSubscriptionModel.channel_id,
            )
            .where(*conditions)
            .distinct()
        )
        return list(result.scalars().all())
