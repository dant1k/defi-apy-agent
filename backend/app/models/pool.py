"""Pool models"""
from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pool(Base):
    """Pool table"""
    __tablename__ = "pool"
    
    id = Column(String(255), primary_key=True, nullable=False)  # Pool address or unique ID
    dex_slug = Column(String(255), ForeignKey("dex.slug"), nullable=False, index=True)
    chain = Column(String(100), nullable=False, index=True)
    token0_address = Column(String(255), nullable=True)
    token0_symbol = Column(String(50), nullable=True)
    token1_address = Column(String(255), nullable=True)
    token1_symbol = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True, index=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_pool_dex_slug", "dex_slug"),
        Index("idx_pool_chain", "chain"),
        Index("idx_pool_address", "address"),
        UniqueConstraint("id", name="uq_pool_id"),
    )


class PoolMetricsDaily(Base):
    """Pool daily metrics table"""
    __tablename__ = "pool_metrics_daily"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pool_id = Column(String(255), ForeignKey("pool.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    tvl_usd = Column(Numeric(20, 2), nullable=True)
    volume_24h_usd = Column(Numeric(20, 2), nullable=True)
    fees_24h_usd = Column(Numeric(20, 2), nullable=True)
    fees_source = Column(String(50), nullable=True)  # "dexscreener" | "aptos_indexer" | null
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_pool_metrics_pool_id", "pool_id"),
        Index("idx_pool_metrics_date", "date"),
        UniqueConstraint("pool_id", "date", name="uq_pool_metrics_pool_date"),
    )
