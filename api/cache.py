"""Utilities for working with Redis-backed strategy cache."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Dict, List, Optional

from redis.asyncio import Redis

try:  # pragma: no cover - optional dependency for collector constants
    from collector.config import (
        CHAIN_SET_KEY,
        LATEST_STRATEGIES_KEY,
        PROTOCOL_SET_KEY,
        STRATEGY_ITEM_HASH,
        STRATEGY_TVL_PREFIX,
    )
except Exception:  # noqa: BLE001 - fallback when collector package not available
    LATEST_STRATEGIES_KEY = "strategies:latest"
    PROTOCOL_SET_KEY = "strategies:protocols"
    CHAIN_SET_KEY = "strategies:chains"
    STRATEGY_ITEM_HASH = "strategies:items"
    STRATEGY_TVL_PREFIX = "strategies:tvl"


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CACHE_PREFIX = os.getenv("STRATEGY_CACHE_PREFIX", "defi:strategies")
DEFAULT_TTL_SECONDS = int(os.getenv("STRATEGY_CACHE_TTL_SECONDS", "600"))
REFRESH_QUEUE_SUFFIX = os.getenv("STRATEGY_REFRESH_QUEUE_SUFFIX", "refresh-queue")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def strategy_cache_key(token: str, risk_level: str, include_wrappers: bool) -> str:
    normalized_token = token.strip().upper()
    normalized_risk = (risk_level or "any").strip().lower() or "any"
    wrappers_flag = "with" if include_wrappers else "no"
    return f"{CACHE_PREFIX}:strategy:{normalized_token}:{normalized_risk}:{wrappers_flag}"


def _normalize_strategy_id(strategy_id: str) -> str:
    return strategy_id.replace(" ", "").replace("::", ":")


@dataclass
class StrategyCacheEntry:
    key: str
    data: Dict[str, Any]
    updated_at: datetime
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return _utcnow() >= self.expires_at


class StrategyCache:
    """High-level helper for storing and retrieving strategy payloads."""

    def __init__(self, redis: Redis, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds
        self._queue_key = f"{CACHE_PREFIX}:{REFRESH_QUEUE_SUFFIX}"
        self._tokens_key = f"{CACHE_PREFIX}:tokens"

    @property
    def redis(self) -> Redis:
        return self._redis

    async def get_strategy(self, key: str) -> Optional[StrategyCacheEntry]:
        raw = await self._redis.get(key)
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None

        data = payload.get("data")
        updated_at_raw = payload.get("updated_at")
        expires_at_raw = payload.get("expires_at")

        if not isinstance(data, dict) or not updated_at_raw or not expires_at_raw:
            return None

        try:
            updated_at = _parse_iso(updated_at_raw)
            expires_at = _parse_iso(expires_at_raw)
        except ValueError:
            return None

        return StrategyCacheEntry(
            key=key,
            data=data,
            updated_at=updated_at,
            expires_at=expires_at,
        )

    async def set_strategy(
        self,
        key: str,
        data: Dict[str, Any],
        *,
        ttl_seconds: Optional[int] = None,
    ) -> StrategyCacheEntry:
        now = _utcnow()
        ttl = ttl_seconds or self._ttl_seconds
        expires_at = now + timedelta(seconds=ttl)

        payload = {
            "data": data,
            "updated_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }
        await self._redis.set(key, json.dumps(payload), ex=ttl)
        return StrategyCacheEntry(
            key=key,
            data=data,
            updated_at=now,
            expires_at=expires_at,
        )

    async def set_many(self, items: Dict[str, Dict[str, Any]], ttl_seconds: Optional[int] = None) -> None:
        if not items:
            return
        async with self._redis.pipeline(transaction=True) as pipe:
            now = _utcnow()
            ttl = ttl_seconds or self._ttl_seconds
            expires_at = now + timedelta(seconds=ttl)
            expires_iso = expires_at.isoformat()
            updated_iso = now.isoformat()
            for key, data in items.items():
                payload = {
                    "data": data,
                    "updated_at": updated_iso,
                    "expires_at": expires_iso,
                }
                pipe.set(key, json.dumps(payload), ex=ttl)
            await pipe.execute()

    async def enqueue_refresh(self, payload: Dict[str, Any]) -> None:
        await self._redis.lpush(self._queue_key, json.dumps(payload))

    async def pop_refresh_request(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        if timeout > 0:
            result = await self._redis.blpop(self._queue_key, timeout=timeout)
            if result is None:
                return None
            _, raw = result
        else:
            raw = await self._redis.rpop(self._queue_key)
            if raw is None:
                return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def get_tokens(self) -> Optional[Dict[str, Any]]:
        raw = await self._redis.get(self._tokens_key)
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    async def set_tokens(self, tokens: list[Dict[str, Any]], ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds or self._ttl_seconds
        payload = {
            "tokens": tokens,
            "updated_at": _utcnow().isoformat(),
        }
        await self._redis.set(self._tokens_key, json.dumps(payload), ex=ttl)

    async def get_latest_strategies(self) -> Optional[Dict[str, Any]]:
        raw = await self._redis.get(LATEST_STRATEGIES_KEY)
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        items = data.get("items")
        if not isinstance(items, list):
            data["items"] = []
        return data

    async def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        raw = await self._redis.hget(STRATEGY_ITEM_HASH, strategy_id)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    async def get_protocols(self) -> List[str]:
        values = await self._redis.smembers(PROTOCOL_SET_KEY)
        if not values:
            return []
        return sorted(values)

    async def get_chains(self) -> List[str]:
        values = await self._redis.smembers(CHAIN_SET_KEY)
        if not values:
            return []
        return sorted(values)

    async def get_tvl_history(self, strategy_id: str, limit: int = 96) -> List[Dict[str, Any]]:
        safe_id = _normalize_strategy_id(strategy_id)
        key = f"{STRATEGY_TVL_PREFIX}:{safe_id}"
        entries = await self._redis.zrange(key, -limit, -1)
        history: List[Dict[str, Any]] = []
        for entry in entries:
            try:
                point = json.loads(entry)
            except json.JSONDecodeError:
                continue
            if isinstance(point, dict) and "t" in point and "v" in point:
                history.append(point)
        return history


_redis_instance: Optional[Redis] = None


async def get_redis() -> Redis:
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis_instance


@asynccontextmanager
async def get_cache(ttl_seconds: int = DEFAULT_TTL_SECONDS) -> AsyncIterator[StrategyCache]:
    redis = await get_redis()
    cache = StrategyCache(redis, ttl_seconds=ttl_seconds)
    try:
        yield cache
    finally:
        # keep connection open for reuse
        pass


async def close_redis() -> None:
    global _redis_instance
    if _redis_instance is not None:
        await _redis_instance.close()
        _redis_instance = None
