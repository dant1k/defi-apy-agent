"""Analytics utilities for discovering new DeFi pools."""

from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests

from src.coins import get_top_market_tokens
from src.utils.tokens import classify_pair, normalize_pair, parse_tokens

ALL_POOLS_URL = "https://yields.llama.fi/pools"
CHART_URL_TEMPLATE = "https://yields.llama.fi/chart/{pool_id}"
PROTOCOL_URL_TEMPLATE = "https://api.llama.fi/protocol/{slug}"
CHART_CACHE_TTL = timedelta(minutes=30)
PROJECT_URL_CACHE_TTL = timedelta(hours=1)
CHART_FETCH_WORKERS = 8
CANDIDATE_MULTIPLIER = 4
TOKEN_SEARCH_CACHE_TTL = timedelta(minutes=5)

MOMENTUM_TVL_WEIGHT = 0.6
MOMENTUM_APY_WEIGHT = 0.4

@dataclass
class CacheEntry:
    fetched_at: datetime
    data: Any


_chart_cache: Dict[str, CacheEntry] = {}
_project_url_cache: Dict[str, CacheEntry] = {}
_token_search_cache: Dict[str, CacheEntry] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _fetch_chart(pool_id: str) -> List[Dict[str, Any]]:
    response = requests.get(CHART_URL_TEMPLATE.format(pool_id=pool_id), timeout=30)
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", [])
    if not isinstance(data, list):
        return []
    return data


def get_chart(pool_id: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Return cached chart data for a pool."""
    now = _utcnow()
    entry = _chart_cache.get(pool_id)
    if not force_refresh and entry and now - entry.fetched_at < CHART_CACHE_TTL:
        return entry.data

    chart = _fetch_chart(pool_id)
    _chart_cache[pool_id] = CacheEntry(fetched_at=now, data=chart)
    return chart


def get_token_pools(symbol: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    token = symbol.upper()
    now = _utcnow()
    entry = _token_search_cache.get(token)
    if entry and not force_refresh and now - entry.fetched_at < TOKEN_SEARCH_CACHE_TTL:
        return entry.data

    params = {"search": token}
    try:
        response = requests.get(ALL_POOLS_URL, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        if not isinstance(data, list):
            data = []
    except requests.RequestException:
        data = []

    _token_search_cache[token] = CacheEntry(fetched_at=now, data=data)
    return data


def get_project_url(project: Optional[str]) -> Optional[str]:
    if not project:
        return None

    key = project.lower()
    now = _utcnow()
    entry = _project_url_cache.get(key)
    if entry and now - entry.fetched_at < PROJECT_URL_CACHE_TTL:
        return entry.data

    try:
        response = requests.get(PROTOCOL_URL_TEMPLATE.format(slug=key), timeout=15)
        if response.status_code == 200:
            url = response.json().get("url")
            _project_url_cache[key] = CacheEntry(fetched_at=now, data=url)
            return url
    except requests.RequestException:
        pass

    _project_url_cache[key] = CacheEntry(fetched_at=now, data=None)
    return None


def _find_point(chart: List[Dict[str, Any]], target_time: datetime) -> Optional[Dict[str, Any]]:
    """Find the data point closest to target_time but not newer."""
    candidate: Optional[Dict[str, Any]] = None
    for point in chart:
        ts = point.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt <= target_time:
            candidate = point
        else:
            break
    return candidate


def _calculate_change(current: Optional[float], past: Optional[float]) -> Optional[float]:
    if current is None or past is None or past == 0:
        return None
    try:
        return (current - past) / past * 100.0
    except ZeroDivisionError:
        return None


def _calculate_momentum(tvl_change: Optional[float], apy_change: Optional[float]) -> float:
    tvl_component = MOMENTUM_TVL_WEIGHT * (tvl_change or 0.0)
    apy_component = MOMENTUM_APY_WEIGHT * (apy_change or 0.0)
    return tvl_component + apy_component


def _estimate_first_seen(chart: List[Dict[str, Any]]) -> Optional[datetime]:
    if not chart:
        return None
    first = chart[0].get("timestamp")
    if not first:
        return None
    try:
        return datetime.fromisoformat(str(first).replace("Z", "+00:00"))
    except ValueError:
        return None


def _filter_by_symbols(tokens: Sequence[str], tracked: Sequence[str]) -> bool:
    if not tracked:
        return True
    upper_tokens = {token.upper() for token in tokens}
    return any(item.upper() in upper_tokens for item in tracked)


def _filter_by_chain(chain: str, chains: Sequence[str]) -> bool:
    if not chains:
        return True
    return chain.lower() in {chain_name.lower() for chain_name in chains}


def _get_new_pool_candidates(
    symbols: Sequence[str],
    period_days: int,
    min_tvl: float,
    chains: Sequence[str],
    force_refresh: bool,
) -> List[Dict[str, Any]]:
    allowed_symbols = {token["symbol"].upper() for token in get_top_market_tokens(limit=100)}
    requested_symbols = [symbol.upper() for symbol in symbols]
    if not requested_symbols:
        raise ValueError("At least one symbol must be provided")

    tokens_to_fetch = [symbol for symbol in requested_symbols if symbol in allowed_symbols]
    if not tokens_to_fetch:
        raise ValueError("Symbols must be from the top-100 list")

    result: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for symbol in tokens_to_fetch:
        pools = get_token_pools(symbol, force_refresh=force_refresh)
        for pool in pools:
            tvl = float(pool.get("tvlUsd") or 0.0)
            if tvl < min_tvl:
                continue

            count = pool.get("count")
            if not isinstance(count, (int, float)) or count > period_days + 1:
                continue

            pair_symbol = pool.get("symbol") or ""
            tokens = parse_tokens(pair_symbol)
            if not _filter_by_symbols(tokens, requested_symbols):
                continue

            chain = pool.get("chain") or ""
            if not _filter_by_chain(chain, chains):
                continue

            norm_pair = normalize_pair(pair_symbol)
            key = (pool.get("project") or "", norm_pair)

            stored = result.get(key)
            if not stored or tvl > stored.get("tvlUsd", 0):
                result[key] = pool

    return list(result.values())


def _enrich_pool(pool: Dict[str, Any], chart: List[Dict[str, Any]], period_days: int) -> Optional[Dict[str, Any]]:
    pool_id = pool.get("pool")
    if not pool_id or not chart:
        return None

    now_point = chart[-1]
    now_tvl = now_point.get("tvlUsd")
    now_apy = now_point.get("apy")

    target_time = _utcnow() - timedelta(days=period_days)
    past_point = _find_point(chart, target_time)
    if past_point is None and chart:
        past_point = chart[0]
    past_tvl = past_point.get("tvlUsd") if past_point else None
    past_apy = past_point.get("apy") if past_point else None

    tvl_change = _calculate_change(now_tvl, past_tvl)
    apy_change = _calculate_change(now_apy, past_apy)
    momentum = _calculate_momentum(tvl_change, apy_change)

    tokens = parse_tokens(pool.get("symbol") or "")
    category = classify_pair(tokens)
    first_seen = _estimate_first_seen(chart)
    action_url = get_project_url(pool.get("project"))

    return {
        "pool_id": pool_id,
        "pair": normalize_pair(pool.get("symbol") or ""),
        "protocol": pool.get("project"),
        "chain": pool.get("chain"),
        "tvl_usd": float(pool.get("tvlUsd") or 0.0),
        "apy": float(pool.get("apy") or 0.0),
        "tvl_change_pct": tvl_change,
        "apy_change_pct": apy_change,
        "momentum": momentum,
        "category": category,
        "first_seen": first_seen.isoformat() if first_seen else None,
        "action_url": action_url,
    }


def get_new_pools(
    period: str = "7d",
    *,
    min_tvl: float = 5_000_000,
    symbols: Sequence[str] = (),
    chains: Sequence[str] = (),
    sort: str = "momentum",
    limit: int = 50,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    period_map = {"24h": 1, "7d": 7, "30d": 30}
    period_key = period.lower()
    if period_key not in period_map:
        raise ValueError("Unsupported period")

    if not symbols:
        raise ValueError("At least one symbol must be provided")

    days = period_map[period_key]
    min_tvl = float(min_tvl)
    limit = max(1, min(limit, 200))

    candidates = _get_new_pool_candidates(
        symbols=symbols,
        period_days=days,
        min_tvl=min_tvl,
        chains=chains,
        force_refresh=force_refresh,
    )
    if not candidates:
        return {
            "period": period_key,
            "days": days,
            "min_tvl": min_tvl,
            "filters": {
                "symbols": list(symbols),
                "chains": [chain for chain in chains],
            },
            "count": 0,
            "pools": [],
        }

    selected = candidates[: limit * CANDIDATE_MULTIPLIER]

    charts: Dict[str, List[Dict[str, Any]]] = {}

    def fetch_chart(pool: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        pool_id = pool.get("pool")
        if not pool_id:
            return "", []
        return pool_id, get_chart(pool_id, force_refresh=force_refresh)

    with ThreadPoolExecutor(max_workers=min(CHART_FETCH_WORKERS, len(selected))) as executor:
        for pool_id, chart in executor.map(fetch_chart, selected):
            if pool_id:
                charts[pool_id] = chart

    enriched: List[Dict[str, Any]] = []
    for pool in selected:
        pool_id = pool.get("pool")
        if not pool_id:
            continue
        chart = charts.get(pool_id)
        if chart is None:
            continue
        item = _enrich_pool(pool, chart, days)
        if item:
            enriched.append(item)

    sort_key = sort.lower()
    if sort_key == "tvl_change":
        enriched.sort(key=lambda item: item.get("tvl_change_pct") or -math.inf, reverse=True)
    elif sort_key == "apy_change":
        enriched.sort(key=lambda item: item.get("apy_change_pct") or -math.inf, reverse=True)
    else:
        enriched.sort(key=lambda item: item.get("momentum") or -math.inf, reverse=True)

    return {
        "period": period_key,
        "days": days,
        "min_tvl": min_tvl,
        "filters": {
            "symbols": list(symbols),
            "chains": [chain for chain in chains],
        },
        "count": len(enriched),
        "pools": enriched[:limit],
    }
