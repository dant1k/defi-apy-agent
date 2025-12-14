"""Initial schema: dex, dex_metrics_daily, pool, pool_metrics_daily

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dex table
    op.create_table(
        'dex',
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('chain', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('slug'),
        sa.UniqueConstraint('slug', name='uq_dex_slug')
    )
    op.create_index('idx_dex_chain', 'dex', ['chain'], unique=False)
    
    # Create dex_metrics_daily table
    op.create_table(
        'dex_metrics_daily',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('dex_slug', sa.String(length=255), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('tvl_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('volume_24h_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('fees_24h_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dex_slug', 'date', name='uq_dex_metrics_dex_date')
    )
    op.create_index('idx_dex_metrics_dex_slug', 'dex_metrics_daily', ['dex_slug'], unique=False)
    op.create_index('idx_dex_metrics_date', 'dex_metrics_daily', ['date'], unique=False)
    
    # Create pool table
    op.create_table(
        'pool',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('dex_slug', sa.String(length=255), nullable=False),
        sa.Column('chain', sa.String(length=100), nullable=False),
        sa.Column('token0_address', sa.String(length=255), nullable=True),
        sa.Column('token0_symbol', sa.String(length=50), nullable=True),
        sa.Column('token1_address', sa.String(length=255), nullable=True),
        sa.Column('token1_symbol', sa.String(length=50), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['dex_slug'], ['dex.slug'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id', name='uq_pool_id')
    )
    op.create_index('idx_pool_dex_slug', 'pool', ['dex_slug'], unique=False)
    op.create_index('idx_pool_chain', 'pool', ['chain'], unique=False)
    op.create_index('idx_pool_address', 'pool', ['address'], unique=False)
    
    # Create pool_metrics_daily table
    op.create_table(
        'pool_metrics_daily',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pool_id', sa.String(length=255), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('tvl_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('volume_24h_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('fees_24h_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['pool_id'], ['pool.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pool_id', 'date', name='uq_pool_metrics_pool_date')
    )
    op.create_index('idx_pool_metrics_pool_id', 'pool_metrics_daily', ['pool_id'], unique=False)
    op.create_index('idx_pool_metrics_date', 'pool_metrics_daily', ['date'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_pool_metrics_date', table_name='pool_metrics_daily')
    op.drop_index('idx_pool_metrics_pool_id', table_name='pool_metrics_daily')
    op.drop_table('pool_metrics_daily')
    op.drop_index('idx_pool_address', table_name='pool')
    op.drop_index('idx_pool_chain', table_name='pool')
    op.drop_index('idx_pool_dex_slug', table_name='pool')
    op.drop_table('pool')
    op.drop_index('idx_dex_metrics_date', table_name='dex_metrics_daily')
    op.drop_index('idx_dex_metrics_dex_slug', table_name='dex_metrics_daily')
    op.drop_table('dex_metrics_daily')
    op.drop_index('idx_dex_chain', table_name='dex')
    op.drop_table('dex')

