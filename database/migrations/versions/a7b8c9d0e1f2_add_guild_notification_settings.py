"""Add per-guild notification settings.

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("guilds", sa.Column("ignore_bots", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column(
        "guilds",
        sa.Column(
            "join_template",
            sa.String(length=500),
            server_default="{user} вошёл в канал «{channel}»",
            nullable=False,
        ),
    )
    op.add_column(
        "guilds",
        sa.Column(
            "leave_template",
            sa.String(length=500),
            server_default="{user} вышел из канала «{channel}»",
            nullable=False,
        ),
    )
    op.add_column(
        "guilds",
        sa.Column(
            "switch_template",
            sa.String(length=500),
            server_default="{user} перешёл из канала «{from_channel}» в «{channel}»",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("guilds", "switch_template")
    op.drop_column("guilds", "leave_template")
    op.drop_column("guilds", "join_template")
    op.drop_column("guilds", "ignore_bots")
