"""add_exploding_gradient_enum

Revision ID: bc22cae41d0a
Revises: 20cfdee47f8b
Create Date: 2026-05-03 20:57:29.317452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc22cae41d0a'
down_revision: Union[str, None] = '20cfdee47f8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot be run inside a transaction block
    op.execute("ALTER TYPE eventtype ADD VALUE 'EXPLODING_GRADIENT'")


def downgrade() -> None:
    # Postgres doesn't easily support removing enum values
    pass
