from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class DsUserModel(BaseModel):
    __tablename__ = "discord_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(70), nullable=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=True)
