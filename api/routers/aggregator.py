"""Endpoints for the AI DeFi strategy aggregator."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from collector.pipeline import collect_and_store

from ..cache import StrategyCache
from ..dependencies import get_strategy_cache


router = APIRouter()


def _parse_csv(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    parts = [chunk.strip() for chunk in value.split(",") if chunk.strip()]
    return parts or None


def _apply_filters(items: List[Dict[str, Any]], *, chain: Optional[List[str]] = None, protocol: Optional[List[str]] = None, min_tvl: Optional[float] = None, min_apy: Optional[float] = None) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for item in items:
        if chain and (item.get("chain") or "").strip().lower() not in {c.lower() for c in chain}:
            continue
        if protocol and (item.get("protocol") or "").strip().lower() not in {p.lower() for p in protocol}:
            continue
        if min_tvl is not None and float(item.get("tvl_usd") or 0.0) < min_tvl:
            continue
        if min_apy is not None and float(item.get("apy") or 0.0) < min_apy:
            continue
        result.append(item)
    return result


def _sort_items(items: List[Dict[str, Any]], sort: str) -> List[Dict[str, Any]]:
    sort_map = {
        "apy_desc": lambda x: (float(x.get("apy") or 0.0), float(x.get("tvl_usd") or 0.0)),
        "tvl_desc": lambda x: (float(x.get("tvl_usd") or 0.0), float(x.get("apy") or 0.0)),
        "ai_score_desc": lambda x: (float(x.get("ai_score") or 0.0), float(x.get("tvl_usd") or 0.0)),
        "tvl_growth_desc": lambda x: (float(x.get("tvl_growth_24h") or 0.0), float(x.get("apy") or 0.0)),
    }
    key_func = sort_map.get(sort, sort_map["ai_score_desc"])
    return sorted(items, key=key_func, reverse=True)


@router.get("/strategies")
async def list_strategies(
    chain: Optional[str] = Query(None, description="Filter by chain, comma separated"),
    protocol: Optional[str] = Query(None, description="Filter by protocol, comma separated"),
    min_tvl: Optional[float] = Query(None, ge=0, description="Minimum TVL in USD"),
    min_apy: Optional[float] = Query(None, ge=0, description="Minimum APY"),
    sort: str = Query("ai_score_desc", description="Sort order: ai_score_desc, apy_desc, tvl_desc, tvl_growth_desc"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    cache: StrategyCache = Depends(get_strategy_cache),
) -> Dict[str, Any]:
    snapshot = await cache.get_latest_strategies()
    if not snapshot:
        raise HTTPException(status_code=503, detail="Нет данных. Запусти обновление и попробуй снова.")

    items = snapshot.get("items", [])
    filtered = _apply_filters(
        items,
        chain=_parse_csv(chain),
        protocol=_parse_csv(protocol),
        min_tvl=min_tvl,
        min_apy=min_apy,
    )
    sorted_items = _sort_items(filtered, sort)
    sliced = sorted_items[offset : offset + limit]

    return {
        "updated_at": snapshot.get("updated_at"),
        "total": len(sorted_items),
        "limit": limit,
        "offset": offset,
        "items": sliced,
    }


@router.get("/strategies/top")
async def top_strategies(
    limit: int = Query(10, ge=1, le=50),
    cache: StrategyCache = Depends(get_strategy_cache),
) -> Dict[str, Any]:
    snapshot = await cache.get_latest_strategies()
    if not snapshot:
        raise HTTPException(status_code=503, detail="Нет данных." )
    items = snapshot.get("items", [])
    sorted_items = _sort_items(items, "ai_score_desc")[:limit]
    return {
        "updated_at": snapshot.get("updated_at"),
        "items": sorted_items,
    }


@router.get("/protocols")
async def list_protocols(cache: StrategyCache = Depends(get_strategy_cache)) -> Dict[str, Any]:
    protocols = await cache.get_protocols()
    return {"count": len(protocols), "items": protocols}


@router.get("/chains")
async def list_chains(cache: StrategyCache = Depends(get_strategy_cache)) -> Dict[str, Any]:
    chains = await cache.get_chains()
    return {"count": len(chains), "items": chains}


@router.get("/refresh")
async def refresh_data() -> Dict[str, Any]:
    stats = await asyncio.to_thread(collect_and_store)
    return {"status": "ok", "details": stats}


@router.get("/strategies/{strategy_id}")
async def strategy_details(
    strategy_id: str = Path(..., description="Unique strategy identifier"),
    history_limit: int = Query(96, ge=1, le=288, description="Number of TVL points to return"),
    cache: StrategyCache = Depends(get_strategy_cache),
) -> Dict[str, Any]:
    item = await cache.get_strategy(strategy_id)
    if not item:
        raise HTTPException(status_code=404, detail="Стратегия не найдена")
    history = await cache.get_tvl_history(strategy_id, limit=history_limit)
    return {"strategy": item, "history": history}
