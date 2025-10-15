"""Strategies and tokens endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ..cache import StrategyCache, StrategyCacheEntry, strategy_cache_key
from ..dependencies import get_strategy_cache
from ..schemas import PreferencesModel, StrategyRequest, StrategyResponse, STALE_AFTER


router = APIRouter()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _extract_preferences(payload: StrategyRequest) -> PreferencesModel:
    if payload.preferences is not None:
        return payload.preferences
    return PreferencesModel()


def _normalize_token(value: str) -> str:
    return value.strip().upper()


def _needs_refresh(entry: Optional[StrategyCacheEntry]) -> bool:
    if not entry:
        return True
    if entry.is_expired:
        return True
    age = _now() - entry.updated_at
    return age >= STALE_AFTER


def _cache_headers(entry: Optional[StrategyCacheEntry]) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Cache-Control": "public, max-age=60, stale-while-revalidate=120",
    }
    if entry:
        headers["X-Strategy-Updated-At"] = entry.updated_at.isoformat()
        headers["X-Strategy-Expires-At"] = entry.expires_at.isoformat()
        headers["X-Strategy-Cache-Hit"] = "1"
    else:
        headers["X-Strategy-Cache-Hit"] = "0"
    return headers


def _refresh_payload(key: str, request_payload: StrategyRequest) -> Dict[str, str]:
    body = request_payload.model_dump()
    return {"key": key, "request": body}


@router.get("/tokens")
async def tokens_list(
    limit: int = Query(100, ge=1, le=200),
    force: bool = Query(False, description="Игнорировать кэш и получить свежие данные"),
    cache: StrategyCache = Depends(get_strategy_cache),
) -> JSONResponse:
    cached_tokens = None if force else await cache.get_tokens()
    if cached_tokens:
        response = JSONResponse(
            content=cached_tokens,
            headers={"Cache-Control": "public, max-age=300, stale-while-revalidate=600"},
        )
        response.headers["X-Token-Cache-Hit"] = "1"
        return response

    # Import lazily so monkeypatching `src.api.get_top_market_tokens` keeps working.
    from src.api import get_top_market_tokens as fetch_tokens

    tokens = fetch_tokens(limit=limit, force_refresh=force)
    payload = {"tokens": tokens}
    await cache.set_tokens(tokens)

    response = JSONResponse(
        content=payload,
        headers={"Cache-Control": "public, max-age=120, stale-while-revalidate=300"},
    )
    response.headers["X-Token-Cache-Hit"] = "0"
    return response


@router.post("/strategies", response_model=StrategyResponse, response_model_exclude_none=True)
async def get_strategies(
    payload: StrategyRequest,
    cache: StrategyCache = Depends(get_strategy_cache),
) -> JSONResponse:
    token = _normalize_token(payload.token)
    if not token:
        raise HTTPException(status_code=400, detail="Поле token не может быть пустым")

    preferences = _extract_preferences(payload)
    risk_level = preferences.risk_level or "any"
    include_wrappers = True if preferences.include_wrappers is None else preferences.include_wrappers

    cache_key = strategy_cache_key(token, risk_level, include_wrappers)
    entry = await cache.get_strategy(cache_key)

    if _needs_refresh(entry) or payload.force_refresh:
        refresh_payload = _refresh_payload(cache_key, payload)
        await cache.enqueue_refresh(refresh_payload)

    if entry is None:
        headers = _cache_headers(entry)
        response = StrategyResponse(
            status="empty",
            token=token,
            message="Данные по стратегии ещё собираются, повторите запрос позже.",
            warnings=["fresh-data-requested"],
        )
        return JSONResponse(
            status_code=202,
            content=response.model_dump(exclude_none=True),
            headers=headers,
        )

    return JSONResponse(
        content=entry.data,
        headers=_cache_headers(entry),
    )


@router.get("/analytics/new-pools")
async def analytics_new_pools(
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
    min_tvl: float = Query(5_000_000, ge=0),
    symbols: List[str] = Query(..., alias="symbols", min_items=1),
    chains: Optional[List[str]] = Query(None, alias="chains"),
    sort: str = Query("momentum", pattern="^(momentum|tvl_change|apy_change)$"),
    limit: int = Query(50, ge=1, le=200),
    force_refresh: bool = False,
) -> Dict[str, Any]:
    from src.api import get_new_pools as fetch_new_pools

    data = fetch_new_pools(
        period,
        min_tvl=min_tvl,
        symbols=symbols,
        chains=chains or (),
        sort=sort,
        limit=limit,
        force_refresh=force_refresh,
    )
    return data
