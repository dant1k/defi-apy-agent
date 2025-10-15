"""Utilities for persisting strategies to Redis."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Tuple

import redis

from .config import (
    CHAIN_SET_KEY,
    LATEST_STRATEGIES_KEY,
    LATEST_TTL_SECONDS,
    PROTOCOL_SET_KEY,
    REDIS_URL,
    STRATEGY_HISTORY_HASH,
    STRATEGY_ITEM_HASH,
    STRATEGY_TVL_PREFIX,
)


class StrategyStorage:
    """Lightweight helper around Redis for storing strategy snapshots."""

    def __init__(self, redis_url: str = REDIS_URL) -> None:
        self.redis = redis.StrictRedis.from_url(redis_url, decode_responses=True)

    def close(self) -> None:
        self.redis.close()

    def load_previous_snapshot(self, strategy_id: str) -> Dict | None:
        raw = self.redis.hget(STRATEGY_HISTORY_HASH, strategy_id)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def save_snapshot(self, strategy_id: str, payload: Dict) -> None:
        self.redis.hset(STRATEGY_HISTORY_HASH, strategy_id, json.dumps(payload))

    def append_tvl_point(self, strategy_id: str, timestamp: datetime, tvl_usd: float) -> None:
        key = tvl_key(strategy_id)
        score = timestamp.timestamp()
        value = json.dumps({"t": timestamp.isoformat(), "v": tvl_usd})
        with self.redis.pipeline() as pipe:
            pipe.zadd(key, {value: score})
            pipe.zremrangebyrank(key, 0, -97)  # keep last 96 entries (~24h at 15m intervals)
            pipe.expire(key, LATEST_TTL_SECONDS * 4)
            pipe.execute()

    def save_latest(self, strategies: List[Dict]) -> None:
        envelope = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(strategies),
            "items": strategies,
        }
        self.redis.setex(LATEST_STRATEGIES_KEY, LATEST_TTL_SECONDS, json.dumps(envelope))

        protocols = {item["protocol"] for item in strategies if item.get("protocol")}
        chains = {item["chain"] for item in strategies if item.get("chain")}

        if protocols:
            self.redis.delete(PROTOCOL_SET_KEY)
            self.redis.sadd(PROTOCOL_SET_KEY, *protocols)
        if chains:
            self.redis.delete(CHAIN_SET_KEY)
            self.redis.sadd(CHAIN_SET_KEY, *chains)

        self.redis.delete(STRATEGY_ITEM_HASH)
        if strategies:
            with self.redis.pipeline() as pipe:
                for item in strategies:
                    pipe.hset(STRATEGY_ITEM_HASH, item["id"], json.dumps(item))
                pipe.execute()

    def get_top_by_score(self, strategies: Iterable[Dict], limit: int = 10) -> List[Dict]:
        sorted_items = sorted(
            strategies,
            key=lambda item: (item.get("ai_score") or 0, item.get("score") or 0),
            reverse=True,
        )
        return sorted_items[:limit]


def compute_growth(
    storage: StrategyStorage,
    strategy_id: str,
    current_value: float,
    now: datetime,
) -> Tuple[float, Dict[str, float]]:
    """Return TVL growth percentage and snapshot payload for persistence."""
    previous = storage.load_previous_snapshot(strategy_id)
    if not previous:
        snapshot = {"tvl_usd": current_value, "timestamp": now.isoformat()}
        return 0.0, snapshot

    prev_value = float(previous.get("tvl_usd") or 0.0)
    prev_ts_raw = previous.get("timestamp")
    try:
        prev_ts = datetime.fromisoformat(prev_ts_raw)
    except Exception:
        prev_ts = now - timedelta(days=1)

    if prev_value <= 0:
        growth = 0.0
    else:
        growth = ((current_value - prev_value) / prev_value) * 100

    if now - prev_ts < timedelta(hours=1):
        # Avoid recalculating growth too frequently; treat as zero change.
        growth = max(growth, 0.0)

    snapshot = {"tvl_usd": current_value, "timestamp": now.isoformat()}
    return growth, snapshot


def tvl_key(strategy_id: str) -> str:
    safe_id = strategy_id.replace(" ", "").replace("::", ":")
    return f"{STRATEGY_TVL_PREFIX}:{safe_id}"
