"""Схемы данных для Aptos DEX метрик."""

from __future__ import annotations

from typing import Dict, Literal

from pydantic import BaseModel, Field

Timeframe = Literal["24h", "7d", "30d", "all"]


class DexSummary(BaseModel):
    """Сводка по DEX протоколу на Aptos."""

    name: str = Field(..., description="Название DEX протокола")
    slug: str = Field(..., description="Уникальный идентификатор (например, 'thala', 'liquidswap')")
    chain: str = Field(default="aptos", description="Блокчейн (всегда 'aptos')")
    tvl_usd: float = Field(..., ge=0, description="Total Value Locked в USD")
    volume: Dict[Timeframe, float] = Field(
        ..., description="Объем торговли по временным периодам"
    )
    fees: Dict[Timeframe, float] = Field(
        ..., description="Комиссии по временным периодам"
    )


class PoolSummary(BaseModel):
    """Сводка по пулу ликвидности на Aptos DEX."""

    id: str = Field(..., description="Уникальный идентификатор пула (например, 'thala-apt-usdc-005')")
    dex_slug: str = Field(..., description="Slug DEX протокола, к которому относится пул")
    address: str = Field(..., description="Адрес пула в сети Aptos")
    token0: str = Field(..., description="Первый токен пары (например, 'APT')")
    token1: str = Field(..., description="Второй токен пары (например, 'USDC')")
    pair: str = Field(..., description="Название пары (например, 'APT-USDC')")
    fee_tier: float = Field(..., ge=0, description="Уровень комиссии пула (например, 0.05 для 0.05%)")
    tvl_usd: float = Field(..., ge=0, description="Total Value Locked пула в USD")
    volume: Dict[Timeframe, float] = Field(
        ..., description="Объем торговли пула по временным периодам"
    )
    fees: Dict[Timeframe, float] = Field(
        ..., description="Комиссии пула по временным периодам"
    )
    apr_fee: float = Field(
        ..., ge=0, description="APR от комиссий (рассчитывается из fees и tvl)"
    )

