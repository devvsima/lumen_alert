from sqlalchemy import delete, exists, select
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
    async def get_guild_settings(session: AsyncSession, guild_id: int) -> GuildModel | None:
        return await session.get(GuildModel, guild_id)

    @staticmethod
    async def update_guild_settings(
        session: AsyncSession, guild_id: int, **values
    ) -> GuildModel | None:
        guild = await session.get(GuildModel, guild_id)
        if guild is None:
            return None
        for field, value in values.items():
            if field not in {"ignore_bots", "join_template", "leave_template", "switch_template"}:
                raise ValueError(f"Unsupported guild setting: {field}")
            setattr(guild, field, value)
        await session.commit()
        return guild

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
    async def ensure_default_subscriptions(session: AsyncSession, user_id: int) -> None:
        user = await session.get(TgUserModel, user_id)
        if user is None or user.sources_configured:
            return
        channels = (
            await session.execute(
                select(DiscordChannelModel).where(DiscordChannelModel.is_enabled.is_(True))
            )
        ).scalars()
        for channel in channels:
            session.add(
                TelegramSourceSubscriptionModel(
                    user_id=user_id,
                    guild_id=channel.guild_id,
                    channel_id=channel.id,
                )
            )
        user.sources_configured = True
        await session.commit()

    @staticmethod
    async def set_guild_subscriptions(
        session: AsyncSession, user_id: int, guild_id: int, enabled: bool
    ) -> None:
        channels = await DiscordSource.get_channels(session, guild_id)
        await session.execute(
            delete(TelegramSourceSubscriptionModel).where(
                TelegramSourceSubscriptionModel.user_id == user_id,
                TelegramSourceSubscriptionModel.guild_id == guild_id,
            )
        )
        if enabled:
            session.add_all(
                [
                    TelegramSourceSubscriptionModel(
                        user_id=user_id, guild_id=guild_id, channel_id=channel.id
                    )
                    for channel in channels
                ]
            )
        await session.commit()

    @staticmethod
    async def subscribe_guild_if_missing(
        session: AsyncSession, user_id: int, guild_id: int
    ) -> bool | None:
        if await session.get(GuildModel, guild_id) is None:
            return None
        existing = await session.scalar(
            select(TelegramSourceSubscriptionModel.channel_id)
            .where(
                TelegramSourceSubscriptionModel.user_id == user_id,
                TelegramSourceSubscriptionModel.guild_id == guild_id,
            )
            .limit(1)
        )
        if existing is not None:
            return False
        channels = await DiscordSource.get_channels(session, guild_id)
        if not channels:
            return False
        session.add_all(
            [
                TelegramSourceSubscriptionModel(
                    user_id=user_id, guild_id=guild_id, channel_id=channel.id
                )
                for channel in channels
            ]
        )
        user = await session.get(TgUserModel, user_id)
        if user is not None:
            user.sources_configured = True
        await session.commit()
        return True

    @staticmethod
    async def toggle_channel(
        session: AsyncSession, user_id: int, guild_id: int, channel_id: int
    ) -> bool:
        query = select(TelegramSourceSubscriptionModel).join(DiscordChannelModel).where(
            TelegramSourceSubscriptionModel.user_id == user_id,
            TelegramSourceSubscriptionModel.guild_id == guild_id,
            TelegramSourceSubscriptionModel.channel_id == channel_id,
            DiscordChannelModel.guild_id == guild_id,
            DiscordChannelModel.is_enabled.is_(True),
        )
        subscription = (await session.execute(query)).scalar_one_or_none()
        if subscription is None:
            channel = await session.get(DiscordChannelModel, channel_id)
            if (
                channel is None
                or channel.guild_id != guild_id
                or not channel.is_enabled
            ):
                return False
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
        user_conditions = [
            TgUserModel.is_alert == True,
            TgUserModel.status >= TgUserStatus.TgUser,
        ]
        if alert_field is not None:
            if alert_field not in {"alert_on_join", "alert_on_leave", "alert_on_switch"}:
                raise ValueError(f"Unsupported alert field: {alert_field}")
            user_conditions.append(getattr(TgUserModel, alert_field) == True)
        enabled_channel = (
            select(DiscordChannelModel.id)
            .where(
                DiscordChannelModel.id.in_(channel_ids),
                DiscordChannelModel.guild_id == guild_id,
                DiscordChannelModel.is_enabled.is_(True),
            )
            .subquery()
        )
        default_users = await session.execute(
            select(TgUserModel.id).where(
                *user_conditions,
                TgUserModel.sources_configured == False,
                exists(
                    select(DiscordChannelModel.id).where(
                        DiscordChannelModel.id.in_(channel_ids),
                        DiscordChannelModel.guild_id == guild_id,
                        DiscordChannelModel.is_enabled == True,
                    )
                ),
            )
        )
        subscribed_users = await session.execute(
            select(TelegramSourceSubscriptionModel.user_id)
            .join(TgUserModel, TgUserModel.id == TelegramSourceSubscriptionModel.user_id)
            .where(
                *user_conditions,
                TgUserModel.sources_configured.is_(True),
                TelegramSourceSubscriptionModel.guild_id == guild_id,
                TelegramSourceSubscriptionModel.channel_id.in_(select(enabled_channel.c.id)),
            )
            .distinct()
        )
        return sorted(
            set(default_users.scalars().all()) | set(subscribed_users.scalars().all())
        )
