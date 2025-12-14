"""DEX models"""
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class Dex(Base):
    """DEX table"""
    __tablename__ = "dex"
    
    slug = Column(String(255), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    chain = Column(String(100), nullable=False, index=True)
    url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_dex_chain", "chain"),
        UniqueConstraint("slug", name="uq_dex_slug"),
    )


class DexMetricsDaily(Base):
    """DEX daily metrics table"""
    __tablename__ = "dex_metrics_daily"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dex_slug = Column(String(255), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    tvl_usd = Column(Numeric(20, 2), nullable=True)
    volume_24h_usd = Column(Numeric(20, 2), nullable=True)
    fees_24h_usd = Column(Numeric(20, 2), nullable=True)  # From DefiLlama
    fees_7d_usd = Column(Numeric(20, 2), nullable=True)  # From DefiLlama
    fees_30d_usd = Column(Numeric(20, 2), nullable=True)  # From DefiLlama
    cumulative_fees_usd = Column(Numeric(20, 2), nullable=True)  # From DefiLlama (totalFees)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_dex_metrics_dex_slug", "dex_slug"),
        Index("idx_dex_metrics_date", "date"),
        UniqueConstraint("dex_slug", "date", name="uq_dex_metrics_dex_date"),
    )
