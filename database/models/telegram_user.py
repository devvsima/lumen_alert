from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class TgUserStatus:
    Banned = 0
    TgUser = 1
    Sponsor = 2
    Moderator = 3
    Admin = 4
    Owner = 5


class TgUserModel(BaseModel):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(70), nullable=True)
    language: Mapped[str] = mapped_column(String(10), server_default="en")
    referral: Mapped[int] = mapped_column(Integer, server_default="0")
    status: Mapped[int] = mapped_column(Integer, server_default="1")
    is_alert: Mapped[bool] = mapped_column(Boolean, server_default="True")

    groups = relationship("GroupMemberModel", back_populates="user")
