from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class DiscordChannelModel(BaseModel):
    __tablename__ = "discord_channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, server_default="True", nullable=False)


class TelegramSourceSubscriptionModel(BaseModel):
    __tablename__ = "telegram_source_subscriptions"
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("telegram_users.id", ondelete="CASCADE"), primary_key=True
    )
    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guilds.id", ondelete="CASCADE"), primary_key=True
    )
    channel_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("discord_channels.id", ondelete="CASCADE"),
        primary_key=True,
    )
