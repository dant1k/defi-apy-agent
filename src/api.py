"""FastAPI приложение для работы с DeFi APY агентом."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncio

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.analytics import get_new_pools
from src.app import run_agent
from src.coins import get_top_market_tokens
from src.pool_index import start_preload_index
from src.utils.constants import SUPPORTED_RISK_LEVELS


class PreferencesModel(BaseModel):
    min_apy: Optional[float] = Field(None, ge=0, description="Минимальный APY")
    risk_level: Optional[str] = Field(
        None, description="Допустимый уровень риска: низкий / средний / высокий"
    )
    max_lockup_days: Optional[int] = Field(
        None, ge=0, description="Максимальный период блокировки (дни)"
    )
    min_tvl: Optional[float] = Field(
        None,
        ge=0,
        description="Минимальный TVL (если <100000 трактуется как миллионы USD)",
    )
    preferred_chains: Optional[list[str]] = Field(
        default=None, description="Предпочитаемые сети (например, ethereum, arbitrum)"
    )
    include_wrappers: Optional[bool] = Field(
        default=True, description="Учитывать обёрнутые токены (wETH, stETH и т.д.)"
    )

    @field_validator("risk_level")
    def _validate_risk_level(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        candidate = value.lower()
        if candidate not in SUPPORTED_RISK_LEVELS:
            raise ValueError(
                f"Неверный уровень риска: {value}. Допустимые: {', '.join(SUPPORTED_RISK_LEVELS)}"
            )
        return candidate


class StrategyRequest(BaseModel):
    token: str = Field(..., description="Тикер токена, например ETH или USDC")
    preferences: Optional[PreferencesModel] = Field(
        default=None, description="Настройки фильтрации и предпочтений"
    )
    result_limit: Optional[int] = Field(
        200, ge=1, le=400, description="Максимальное число стратегий для анализа"
    )
    force_refresh: bool = Field(
        False, description="Игнорировать кэш и загрузить свежие данные"
    )
    debug: bool = Field(False, description="Возвращать отладочную информацию")


class StrategyResponse(BaseModel):
    status: str
    token: Optional[str] = None
    message: Optional[str] = None
    best_strategy: Optional[Dict[str, Any]] = None
    alternatives: Optional[list[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None
    warnings: Optional[list[str]] = None
    debug: Optional[Dict[str, Any]] = None


CACHE_TTL = timedelta(minutes=10)
STALE_AFTER = timedelta(minutes=5)


@dataclass
class StrategyCacheEntry:
    payload: "StrategyRequest"
    data: Dict[str, Any]
    updated_at: datetime
    expires_at: datetime
    refresh_in_progress: bool = False


_strategy_cache: Dict[str, StrategyCacheEntry] = {}


app = FastAPI(title="DeFi APY Agent API", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    start_preload_index()


@app.get("/tokens")
async def tokens_list(limit: int = 100, force: bool = False):
    safe_limit = max(1, min(limit, 200))
    tokens = get_top_market_tokens(limit=safe_limit, force_refresh=force)
    return JSONResponse(
        content={"tokens": tokens},
        headers={"Cache-Control": "public, max-age=300, stale-while-revalidate=300"},
    )


def _strategy_cache_key(payload: StrategyRequest) -> str:
    preferences = payload.preferences.model_dump(exclude_none=True) if payload.preferences else {}
    risk_key = preferences.get("risk_level", "any")
    wrappers_key = preferences.get("include_wrappers", True)
    return f"{payload.token.strip().upper()}|{risk_key}|{wrappers_key}"


async def _execute_strategy(payload: StrategyRequest) -> Dict[str, Any]:
    if not payload.token.strip():
        raise HTTPException(status_code=400, detail="Поле token не может быть пустым")

    preferences: Dict[str, Any] = (
        payload.preferences.model_dump(exclude_none=True) if payload.preferences else {}
    )

    result = await asyncio.to_thread(
        run_agent,
        payload.token.strip(),
        user_preferences=preferences,
        result_limit=payload.result_limit or 200,
        force_refresh=payload.force_refresh,
        debug=payload.debug,
    )
    return result


async def _refresh_cache_entry(key: str, payload: StrategyRequest) -> None:
    entry = _strategy_cache.get(key)
    if entry is None:
        return
    try:
        refreshed_payload = payload.model_copy(deep=True)
        refreshed_payload.force_refresh = True
        data = await _execute_strategy(refreshed_payload)
        now = datetime.utcnow()
        _strategy_cache[key] = StrategyCacheEntry(
            payload=refreshed_payload,
            data=data,
            updated_at=now,
            expires_at=now + CACHE_TTL,
        )
    finally:
        refreshed = _strategy_cache.get(key)
        if refreshed:
            refreshed.refresh_in_progress = False


@app.post("/strategies", response_model=StrategyResponse, response_model_exclude_none=True)
async def get_strategies(
    payload: StrategyRequest, background_tasks: BackgroundTasks
) -> StrategyResponse:
    key = _strategy_cache_key(payload)
    now = datetime.utcnow()
    cached = _strategy_cache.get(key)

    if payload.force_refresh:
        data = await _execute_strategy(payload)
        entry = StrategyCacheEntry(
            payload=payload.model_copy(deep=True),
            data=data,
            updated_at=now,
            expires_at=now + CACHE_TTL,
        )
        _strategy_cache[key] = entry
        return JSONResponse(
            content=data,
            headers={"Cache-Control": "public, max-age=120, stale-while-revalidate=120"},
        )

    if cached and cached.expires_at > now:
        response = StrategyResponse(**cached.data)
        if now - cached.updated_at > STALE_AFTER and not cached.refresh_in_progress:
            cached.refresh_in_progress = True
            background_tasks.add_task(_refresh_cache_entry, key, cached.payload)
        return JSONResponse(
            content=response.model_dump(exclude_none=True),
            headers={"Cache-Control": "public, max-age=60, stale-while-revalidate=120"},
        )

    data = await _execute_strategy(payload)
    entry = StrategyCacheEntry(
        payload=payload.model_copy(deep=True),
        data=data,
        updated_at=now,
        expires_at=now + CACHE_TTL,
    )
    _strategy_cache[key] = entry
    return JSONResponse(
        content=data,
        headers={"Cache-Control": "public, max-age=60, stale-while-revalidate=120"},
    )


@app.get("/analytics/new-pools")
async def analytics_new_pools(
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
    min_tvl: float = Query(5_000_000, ge=0),
    symbols: List[str] = Query(..., alias="symbols", min_items=1),
    chains: Optional[List[str]] = Query(None, alias="chains"),
    sort: str = Query("momentum", pattern="^(momentum|tvl_change|apy_change)$"),
    limit: int = Query(50, ge=1, le=200),
    force_refresh: bool = False,
) -> Dict[str, Any]:
    data = get_new_pools(
        period,
        min_tvl=min_tvl,
        symbols=symbols,
        chains=chains or (),
        sort=sort,
        limit=limit,
        force_refresh=force_refresh,
    )
    return data
