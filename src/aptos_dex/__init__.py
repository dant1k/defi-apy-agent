"""Модуль для работы с метриками Aptos DEX."""

from .schemas import DexSummary, PoolSummary, Timeframe
from .service import (
    DEXES_KEY,
    POOLS_KEY,
    get_aptos_dex_by_slug,
    get_aptos_dexes_from_storage,
    get_aptos_pool_by_id,
    get_aptos_pools_by_dex,
    get_aptos_pools_from_storage,
    save_aptos_dexes_to_storage,
    save_aptos_pools_to_storage,
)

__all__ = [
    # Schemas
    "DexSummary",
    "PoolSummary",
    "Timeframe",
    # Service functions
    "get_aptos_dexes_from_storage",
    "get_aptos_pools_from_storage",
    "save_aptos_dexes_to_storage",
    "save_aptos_pools_to_storage",
    "get_aptos_dex_by_slug",
    "get_aptos_pool_by_id",
    "get_aptos_pools_by_dex",
    # Keys
    "DEXES_KEY",
    "POOLS_KEY",
]

