"""Pydantic schemas shared between API and worker."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.utils.constants import SUPPORTED_RISK_LEVELS


CACHE_TTL = timedelta(minutes=10)
STALE_AFTER = timedelta(minutes=5)


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
    @classmethod
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
    model_config = ConfigDict(extra="allow")

    status: str
    token: Optional[str] = None
    message: Optional[str] = None
    best_strategy: Optional[Dict[str, Any]] = None
    alternatives: Optional[list[Dict[str, Any]]] = None
    all_strategies: Optional[list[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None
    warnings: Optional[list[str]] = None
    debug: Optional[Dict[str, Any]] = None


class CachedStrategyPayload(BaseModel):
    data: StrategyResponse
    updated_at: float
    ttl_seconds: int
