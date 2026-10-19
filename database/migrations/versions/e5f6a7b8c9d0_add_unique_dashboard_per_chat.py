"""Allow only one dashboard per Telegram chat.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM dashboards
        WHERE id NOT IN (
            SELECT MAX(id) FROM dashboards GROUP BY chat_id
        )
        """
    )
    op.create_index("uq_dashboard_chat", "dashboards", ["chat_id"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_dashboard_chat", table_name="dashboards")
