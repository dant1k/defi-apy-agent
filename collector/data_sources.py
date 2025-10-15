"""Raw data fetchers for supported protocols."""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List

import requests

from .config import (
    BEEFY_APY_URL,
    BEEFY_VAULTS_URL,
    COINGECKO_MARKET_URL,
    COINGECKO_PAGES,
    COINGECKO_PER_PAGE,
    COINGECKO_VS_CURRENCY,
    DEFILLAMA_PROTOCOLS_URL,
    DEFILLAMA_YIELDS_URL,
    HTTP_TIMEOUT_SECONDS,
    MORPHO_GRAPHQL_URL,
    PENDLE_YIELD_URL,
    SOMMELIER_VAULTS_URL,
    STAKEDAO_VAULTS_URL,
    YEARN_VAULTS_URL,
)

logger = logging.getLogger(__name__)


def _safe_get(url: str) -> dict | list | None:
    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("Request to %s failed: %s", url, exc)
        return None


def fetch_defillama_pools() -> List[Dict]:
    """Return list of pools from DefiLlama Yields API."""
    payload = _safe_get(DEFILLAMA_YIELDS_URL)
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def fetch_defillama_protocols() -> List[Dict]:
    payload = _safe_get(DEFILLAMA_PROTOCOLS_URL)
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def fetch_beefy_data() -> List[Dict]:
    vaults_payload = _safe_get(BEEFY_VAULTS_URL)
    apy_payload = _safe_get(BEEFY_APY_URL)

    if not isinstance(vaults_payload, list):
        vaults_payload = []
    if not isinstance(apy_payload, dict):
        apy_payload = {}

    result: List[Dict] = []
    for item in vaults_payload:
        if not isinstance(item, dict):
            continue
        vault_id = item.get("id")
        if not vault_id:
            continue
        apy = apy_payload.get(vault_id)
        if apy is None:
            continue
        merged = item.copy()
        merged["apy"] = apy
        result.append(merged)
    return result


def fetch_yearn_vaults() -> List[Dict]:
    payload = _safe_get(YEARN_VAULTS_URL)
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def fetch_sommelier_vaults() -> List[Dict]:
    payload = _safe_get(SOMMELIER_VAULTS_URL)
    if isinstance(payload, dict):
        data = payload.get("vaults") or payload.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def fetch_pendle_yields() -> List[Dict]:
    payload = _safe_get(PENDLE_YIELD_URL)
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def fetch_stakedao_vaults() -> List[Dict]:
    payload = _safe_get(STAKEDAO_VAULTS_URL)
    if isinstance(payload, dict):
        data = payload.get("vaults") or payload.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def fetch_morpho_markets() -> List[Dict]:
    query = {
        "query": """
        query FetchMarkets($limit: Int!) {
          markets(first: $limit) {
            edges {
              node {
                id
                name
                chain
                totalSupplyUSD
                supplyApy
                underlyingTokenAddress
                underlyingTokenSymbol
              }
            }
          }
        }
        """,
        "variables": {"limit": 200},
    }
    try:
        response = requests.post(MORPHO_GRAPHQL_URL, json=query, timeout=HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.warning("Morpho request failed: %s", exc)
        return []

    data = payload.get("data", {})
    markets = data.get("markets", {})
    edges = markets.get("edges", []) if isinstance(markets, dict) else []
    result: List[Dict] = []
    for edge in edges:
        node = edge.get("node") if isinstance(edge, dict) else None
        if isinstance(node, dict):
            result.append(node)
    return result


def iter_all_sources() -> Iterable[tuple[str, List[Dict]]]:
    """Helper to iterate through all configured sources."""
    yield "defillama", fetch_defillama_pools()
    yield "beefy", fetch_beefy_data()
    yield "yearn", fetch_yearn_vaults()
    yield "sommelier", fetch_sommelier_vaults()
    yield "pendle", fetch_pendle_yields()
    yield "stakedao", fetch_stakedao_vaults()
    yield "morpho", fetch_morpho_markets()


def fetch_coingecko_markets() -> List[Dict]:
    markets: List[Dict] = []
    for page in range(1, COINGECKO_PAGES + 1):
        params = {
            "vs_currency": COINGECKO_VS_CURRENCY,
            "order": "market_cap_desc",
            "per_page": str(COINGECKO_PER_PAGE),
            "page": str(page),
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
        }
        try:
            response = requests.get(COINGECKO_MARKET_URL, params=params, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, list):
                markets.extend(item for item in payload if isinstance(item, dict))
        except requests.RequestException as exc:
            logger.warning("Coingecko request failed (page %s): %s", page, exc)
            break
    return markets
