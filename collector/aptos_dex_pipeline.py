"""Пайплайн для сбора и сохранения данных Aptos DEX."""

from __future__ import annotations

from .aptos_dex_sources import fetch_aptos_dexes
from .storage import StrategyStorage

DEXES_KEY = "aptos:dexes"
POOLS_KEY = "aptos:pools"


def collect_and_store_aptos_dex_data() -> None:
    """Собрать и сохранить данные Aptos DEX в Redis."""
    data = fetch_aptos_dexes()
    storage = StrategyStorage()
    try:
        storage.store_json(DEXES_KEY, data["dexes"])
        storage.store_json(POOLS_KEY, data["pools"])
    finally:
        storage.close()

