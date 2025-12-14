"""add_fees_source_to_pool_metrics

Revision ID: 0d6389d6389c
Revises: ac6d0c85ea93
Create Date: 2025-12-13 21:51:57.283761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d6389d6389c'
down_revision: Union[str, None] = 'ac6d0c85ea93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add fees_source column to pool_metrics_daily table
    op.add_column('pool_metrics_daily', sa.Column('fees_source', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove fees_source column from pool_metrics_daily table
    op.drop_column('pool_metrics_daily', 'fees_source')
