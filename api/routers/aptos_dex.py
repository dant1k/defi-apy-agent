"""API роутер для метрик Aptos DEX."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from src.aptos_dex.schemas import DexSummary, PoolSummary, Timeframe
from src.aptos_dex.service import (
    get_aptos_dexes_from_storage,
    get_aptos_pools_from_storage,
    get_aptos_pool_by_id,
)

router = APIRouter(prefix="/aptos", tags=["aptos"])


@router.get("/dexes", response_model=list[DexSummary])
def get_aptos_dexes(
    sort_by: Literal["tvl", "volume", "fees"] = Query("tvl"),
    timeframe: Timeframe = Query("24h"),
    min_tvl: float = Query(0),
):
    """Получить список DEX протоколов Aptos с фильтрацией и сортировкой."""
    dexes = get_aptos_dexes_from_storage()
    filtered = [d for d in dexes if d.tvl_usd >= min_tvl]
    if sort_by == "tvl":
        filtered.sort(key=lambda d: d.tvl_usd, reverse=True)
    elif sort_by == "volume":
        filtered.sort(key=lambda d: d.volume[timeframe], reverse=True)
    elif sort_by == "fees":
        filtered.sort(key=lambda d: d.fees[timeframe], reverse=True)
    return filtered


@router.get("/pools", response_model=list[PoolSummary])
def get_aptos_pools(
    dex: str | None = Query(None),
    pair: str | None = Query(None),
    sort_by: Literal["tvl", "volume", "fees", "apr"] = Query("tvl"),
    timeframe: Timeframe = Query("24h"),
    min_tvl: float = Query(0),
    min_apr: float = Query(0),
):
    """Получить список пулов Aptos DEX с фильтрацией и сортировкой."""
    pools = get_aptos_pools_from_storage()
    if dex:
        pools = [p for p in pools if p.dex_slug == dex]
    if pair:
        pair_upper = pair.upper()
        pools = [p for p in pools if p.pair.upper() == pair_upper]
    pools = [p for p in pools if p.tvl_usd >= min_tvl]
    pools = [p for p in pools if (p.apr_fee * 100) >= min_apr]
    if sort_by == "tvl":
        pools.sort(key=lambda p: p.tvl_usd, reverse=True)
    elif sort_by == "volume":
        pools.sort(key=lambda p: p.volume[timeframe], reverse=True)
    elif sort_by == "fees":
        pools.sort(key=lambda p: p.fees[timeframe], reverse=True)
    elif sort_by == "apr":
        pools.sort(key=lambda p: p.apr_fee, reverse=True)
    return pools


@router.get("/pools/{pool_id}", response_model=PoolSummary)
def get_aptos_pool(pool_id: str):
    """Получить пул по ID."""
    pool = get_aptos_pool_by_id(pool_id)
    if not pool:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool

