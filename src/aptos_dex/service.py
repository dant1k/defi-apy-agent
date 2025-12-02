"""Сервис для работы с метриками Aptos DEX в Redis хранилище."""

from __future__ import annotations

import json
from typing import List, Optional

from collector.storage import StrategyStorage

from .schemas import DexSummary, PoolSummary

DEXES_KEY = "aptos:dexes"
POOLS_KEY = "aptos:pools"


def _get_json(storage: StrategyStorage, key: str) -> Optional[List[dict]]:
    """Вспомогательная функция для получения JSON данных из Redis."""
    raw = storage.redis.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _set_json(storage: StrategyStorage, key: str, data: List[dict], ttl: Optional[int] = None) -> None:
    """Вспомогательная функция для сохранения JSON данных в Redis."""
    json_str = json.dumps(data)
    if ttl:
        storage.redis.setex(key, ttl, json_str)
    else:
        storage.redis.set(key, json_str)


def get_aptos_dexes_from_storage() -> List[DexSummary]:
    """Получить список всех DEX протоколов Aptos из хранилища."""
    storage = StrategyStorage()
    try:
        raw = _get_json(storage, DEXES_KEY) or []
        return [DexSummary(**item) for item in raw]
    finally:
        storage.close()


def get_aptos_pools_from_storage() -> List[PoolSummary]:
    """Получить список всех пулов Aptos DEX из хранилища."""
    storage = StrategyStorage()
    try:
        raw = _get_json(storage, POOLS_KEY) or []
        return [PoolSummary(**item) for item in raw]
    finally:
        storage.close()


def save_aptos_dexes_to_storage(dexes: List[DexSummary], ttl: Optional[int] = None) -> None:
    """Сохранить список DEX протоколов Aptos в хранилище."""
    storage = StrategyStorage()
    try:
        data = [dex.model_dump() for dex in dexes]
        _set_json(storage, DEXES_KEY, data, ttl)
    finally:
        storage.close()


def save_aptos_pools_to_storage(pools: List[PoolSummary], ttl: Optional[int] = None) -> None:
    """Сохранить список пулов Aptos DEX в хранилище."""
    storage = StrategyStorage()
    try:
        data = [pool.model_dump() for pool in pools]
        _set_json(storage, POOLS_KEY, data, ttl)
    finally:
        storage.close()


def get_aptos_dex_by_slug(slug: str) -> Optional[DexSummary]:
    """Получить DEX протокол по slug."""
    dexes = get_aptos_dexes_from_storage()
    for dex in dexes:
        if dex.slug == slug:
            return dex
    return None


def get_aptos_pool_by_id(pool_id: str) -> Optional[PoolSummary]:
    """Получить пул по ID."""
    pools = get_aptos_pools_from_storage()
    for pool in pools:
        if pool.id == pool_id:
            return pool
    return None


def get_aptos_pools_by_dex(dex_slug: str) -> List[PoolSummary]:
    """Получить все пулы для указанного DEX протокола."""
    pools = get_aptos_pools_from_storage()
    return [pool for pool in pools if pool.dex_slug == dex_slug]

