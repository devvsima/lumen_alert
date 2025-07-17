from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class GroupModel(BaseModel):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    group_type: Mapped[str] = mapped_column(String, nullable=True)

    members = relationship("GroupMemberModel", back_populates="group", cascade="all, delete")


class GroupMemberModel(BaseModel):
    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("telegram_users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    group = relationship("GroupModel", back_populates="members")
    user = relationship("UserModel", back_populates="groups")
