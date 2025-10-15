"""FastAPI dependencies."""

from __future__ import annotations

from typing import AsyncIterator

from .cache import StrategyCache, get_cache


async def get_strategy_cache() -> AsyncIterator[StrategyCache]:
    async with get_cache() as cache:
        yield cache
