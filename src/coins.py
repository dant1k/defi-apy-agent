"""Utilities for working with top market tokens."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

COINMARKETCAP_URL = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing"
CMC_CACHE_TTL = timedelta(minutes=30)


@dataclass
class TokensCache:
    fetched_at: datetime
    tokens: List[Dict[str, str]]


_tokens_cache: Optional[TokensCache] = None


def _fetch_top_tokens(limit: int = 100) -> List[Dict[str, str]]:
    params = {"start": "1", "limit": str(limit), "convert": "USD"}
    response = requests.get(COINMARKETCAP_URL, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    data = (payload or {}).get("data", {})
    items = data.get("cryptoCurrencyList", [])

    result: List[Dict[str, str]] = []
    for item in items:
        symbol = (item.get("symbol") or "").upper()
        name = item.get("name") or symbol
        slug = item.get("slug") or symbol.lower()
        if not symbol:
            continue
        result.append({"symbol": symbol, "name": name, "slug": slug})
    return result


def get_top_market_tokens(limit: int = 100, force_refresh: bool = False) -> List[Dict[str, str]]:
    """Return list of top market tokens (symbol, name, slug)."""
    global _tokens_cache

    now = datetime.utcnow()

    if not force_refresh and _tokens_cache and now - _tokens_cache.fetched_at < CMC_CACHE_TTL:
        return _tokens_cache.tokens

    tokens = _fetch_top_tokens(limit=limit)
    _tokens_cache = TokensCache(fetched_at=now, tokens=tokens)
    return tokens
