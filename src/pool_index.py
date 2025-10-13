"""In-memory index of DeFiLlama pools for fast lookups."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, Iterable, List

import requests

from src.utils.tokens import classify_pair, contains_wrapper, normalize_pair, parse_tokens

POOLS_URL = "https://yields.llama.fi/pools"
INDEX_TTL = timedelta(minutes=15)


class PoolIndex:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: Dict[str, List[Dict[str, object]]] = {}
        self._timestamp: datetime | None = None

    def ensure_loaded(self, force: bool = False) -> None:
        with self._lock:
            if not force and self._timestamp and datetime.utcnow() - self._timestamp < INDEX_TTL:
                return

            response = requests.get(POOLS_URL, timeout=30)
            response.raise_for_status()
            payload = response.json()
            pools = payload.get("data", []) if isinstance(payload, dict) else []

            new_index: Dict[str, List[Dict[str, object]]] = {}
            for pool in pools:
                symbol = pool.get("symbol") or ""
                tokens = parse_tokens(symbol)
                category = classify_pair(tokens)
                wrapper_flag = contains_wrapper(tokens)
                normalized = normalize_pair(symbol)

                entry = dict(pool)
                entry["tokens"] = tokens
                entry["category"] = category
                entry["contains_wrapper"] = wrapper_flag
                entry["pair"] = normalized

                for token in tokens:
                    new_index.setdefault(token, []).append(entry)

            self._data = new_index
            self._timestamp = datetime.utcnow()

    def get_pools(self, token: str) -> List[Dict[str, object]]:
        self.ensure_loaded()
        return list(self._data.get(token.upper(), []))


POOL_INDEX = PoolIndex()


def preload_index() -> None:
    try:
        POOL_INDEX.ensure_loaded()
    except Exception:
        pass
