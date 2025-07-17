from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Guild(BaseModel):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)
