"""add_fees_fields_to_dex_metrics

Revision ID: ac6d0c85ea93
Revises: 001_initial
Create Date: 2025-12-13 21:37:29.067288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac6d0c85ea93'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fees fields to dex_metrics_daily table
    op.add_column('dex_metrics_daily', sa.Column('fees_7d_usd', sa.Numeric(precision=20, scale=2), nullable=True))
    op.add_column('dex_metrics_daily', sa.Column('fees_30d_usd', sa.Numeric(precision=20, scale=2), nullable=True))
    op.add_column('dex_metrics_daily', sa.Column('cumulative_fees_usd', sa.Numeric(precision=20, scale=2), nullable=True))


def downgrade() -> None:
    # Remove fees fields from dex_metrics_daily table
    op.drop_column('dex_metrics_daily', 'cumulative_fees_usd')
    op.drop_column('dex_metrics_daily', 'fees_30d_usd')
    op.drop_column('dex_metrics_daily', 'fees_7d_usd')
