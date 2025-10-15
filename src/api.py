"""Backward compatibility layer for legacy imports.

The new API implementation lives in the top-level ``api`` package.  This module
re-exports the FastAPI application and commonly monkeypatched callables so that
existing imports ``from src import api`` keep working (for example, in tests).
"""

from __future__ import annotations

from api import app  # noqa: F401  (re-exported FastAPI app)
from api.schemas import PreferencesModel, StrategyRequest, StrategyResponse
from src.analytics import get_new_pools
from src.app import run_agent
from src.coins import get_top_market_tokens
from src.pool_index import start_preload_index

__all__ = [
    "app",
    "PreferencesModel",
    "StrategyRequest",
    "StrategyResponse",
    "get_top_market_tokens",
    "run_agent",
    "get_new_pools",
    "start_preload_index",
]
