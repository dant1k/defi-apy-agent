"""FastAPI приложение для работы с DeFi APY агентом."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.analytics import get_new_pools
from src.app import run_agent
from src.coins import get_top_market_tokens
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


app = FastAPI(title="DeFi APY Agent API", version="1.0.0")

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


@app.get("/tokens")
async def tokens_list(limit: int = 100, force: bool = False) -> Dict[str, List[Dict[str, str]]]:
    safe_limit = max(1, min(limit, 200))
    tokens = get_top_market_tokens(limit=safe_limit, force_refresh=force)
    return {"tokens": tokens}


@app.post("/strategies", response_model=StrategyResponse, response_model_exclude_none=True)
async def get_strategies(payload: StrategyRequest) -> StrategyResponse:
    if not payload.token.strip():
        raise HTTPException(status_code=400, detail="Поле token не может быть пустым")

    preferences: Dict[str, Any] = (
        payload.preferences.model_dump(exclude_none=True) if payload.preferences else {}
    )

    result = run_agent(
        payload.token.strip(),
        user_preferences=preferences,
        result_limit=payload.result_limit or 200,
        force_refresh=payload.force_refresh,
        debug=payload.debug,
    )

    return StrategyResponse(**result)


@app.get("/analytics/new-pools")
async def analytics_new_pools(
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
    min_tvl: float = Query(5_000_000, ge=0),
    symbols: Optional[List[str]] = Query(None, alias="symbols"),
    chains: Optional[List[str]] = Query(None, alias="chains"),
    sort: str = Query("momentum", pattern="^(momentum|tvl_change|apy_change)$"),
    limit: int = Query(50, ge=1, le=200),
    force_refresh: bool = False,
) -> Dict[str, Any]:
    data = get_new_pools(
        period,
        min_tvl=min_tvl,
        symbols=symbols or (),
        chains=chains or (),
        sort=sort,
        limit=limit,
        force_refresh=force_refresh,
    )
    return data
