from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class GuildModel(BaseModel):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)
    ignore_bots: Mapped[bool] = mapped_column(Boolean, server_default="True", nullable=False)
    join_template: Mapped[str] = mapped_column(
        String(500), server_default="{user} вошёл в канал «{channel}»", nullable=False
    )
    leave_template: Mapped[str] = mapped_column(
        String(500), server_default="{user} вышел из канала «{channel}»", nullable=False
    )
    switch_template: Mapped[str] = mapped_column(
        String(500),
        server_default="{user} перешёл из канала «{from_channel}» в «{channel}»",
        nullable=False,
    )
