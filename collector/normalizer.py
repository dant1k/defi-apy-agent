"""Convert raw protocol payloads into unified strategy records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from .config import DEFAULT_ICON_URL
from .data_sources import fetch_defillama_protocols

# Cache protocol metadata to enhance normalized entries.
_PROTOCOL_META: Dict[str, Dict] | None = None


def _ensure_protocol_meta() -> Dict[str, Dict]:
    global _PROTOCOL_META
    if _PROTOCOL_META is None:
        meta_list = fetch_defillama_protocols()
        _PROTOCOL_META = {}
        for item in meta_list:
            slug = (item.get("slug") or item.get("name") or "").strip().lower()
            if not slug:
                continue
            _PROTOCOL_META[slug] = item
    return _PROTOCOL_META or {}


def _lookup_protocol_icon(protocol: str | None) -> str:
    if not protocol:
        return DEFAULT_ICON_URL
    meta = _ensure_protocol_meta()
    slug_candidates = {protocol.strip().lower()}
    icon = DEFAULT_ICON_URL
    for slug in slug_candidates:
        data = meta.get(slug)
        if not data:
            continue
        symbol = data.get("symbol")
        if symbol:
            icon = f"https://icons.llama.fi/{symbol.lower()}?w=64&h=64"
        logo = data.get("logo")
        if logo:
            icon = logo
        break
    return icon


def _lookup_protocol_url(protocol: str | None) -> str | None:
    """Get protocol website URL from DeFiLlama metadata."""
    if not protocol:
        return None
    meta = _ensure_protocol_meta()
    slug_candidates = {protocol.strip().lower()}
    
    for slug in slug_candidates:
        data = meta.get(slug)
        if not data:
            continue
        
        # Try to get website URL from various possible fields
        url = data.get("url") or data.get("website") or data.get("homepage")
        if url:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            return url
        break
    return None


def normalize_defillama_pool(item: Dict) -> Optional[Dict]:
    pool_id = item.get("pool")
    if not pool_id:
        return None

    apy = float(item.get("apy") or item.get("apyBase") or 0.0)
    tvl_usd = float(item.get("tvlUsd") or 0.0)
    tokens = item.get("symbol") or ""

    protocol = (item.get("project") or "").strip()
    chain = (item.get("chain") or "").strip()

    # Try to get protocol website URL, fallback to DeFiLlama if not available
    protocol_url = _lookup_protocol_url(protocol)
    if not protocol_url:
        protocol_url = f"https://defillama.com/yields/pool/{pool_id}"

    return {
        "id": f"defillama:{pool_id}",
        "source": "defillama",
        "name": item.get("project") or item.get("pool") or "Unknown pool",
        "protocol": protocol or "Unknown",
        "chain": chain or "Unknown",
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,  # placeholder, will be calculated later
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": tokens,
        "url": protocol_url,
        "icon_url": _lookup_protocol_icon(protocol),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "category": item.get("project"),
            "project_id": item.get("projectId"),
            "confidence": item.get("confidence"),
        },
    }


def normalize_beefy_vault(item: Dict) -> Optional[Dict]:
    vault_id = item.get("id")
    if not vault_id:
        return None
    apy_raw = item.get("apy")
    try:
        apy = float(apy_raw) * 100 if apy_raw is not None else 0.0
    except (TypeError, ValueError):
        apy = 0.0

    tvl_usd = float(item.get("tvl") or 0.0)
    chain = (item.get("chain") or "").strip()
    protocol = "Beefy"
    token_pair = " / ".join(item.get("assets") or []) or item.get("symbol") or ""
    return {
        "id": f"beefy:{vault_id}",
        "source": "beefy",
        "name": item.get("name") or vault_id,
        "protocol": protocol,
        "chain": chain or "Unknown",
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": token_pair,
        "url": f"https://app.beefy.finance/#/vault/{vault_id}",
        "icon_url": _lookup_protocol_icon(protocol),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "strategy_type": item.get("strategyType"),
            "platform": item.get("platform"),
        },
    }


def normalize_yearn_vault(item: Dict) -> Optional[Dict]:
    address = item.get("address")
    if not address:
        return None

    chain_id = item.get("chainID") or item.get("chainId") or 1
    chain_name = {1: "Ethereum", 137: "Polygon", 250: "Fantom", 10: "Optimism", 42161: "Arbitrum"}.get(
        chain_id,
        str(chain_id),
    )

    apy_data = item.get("apy") or {}
    net_apy = apy_data.get("net_apy") or 0.0
    try:
        apy = float(net_apy) * 100
    except (TypeError, ValueError):
        apy = 0.0

    tvl_data = item.get("tvl") or {}
    tvl_usd = float(tvl_data.get("tvl") or 0.0)

    symbol = item.get("symbol") or item.get("display_name") or item.get("displayName") or ""
    protocol = "Yearn"

    return {
        "id": f"yearn:{address}",
        "source": "yearn",
        "name": item.get("name") or item.get("display_name") or item.get("displayName") or address,
        "protocol": protocol,
        "chain": chain_name,
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": symbol,
        "url": f"https://yearn.fi/vaults/{chain_id}/{address}",
        "icon_url": _lookup_protocol_icon(protocol),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "decimals": item.get("decimals"),
            "type": item.get("type"),
        },
    }


def normalize_sommelier_vault(item: Dict) -> Optional[Dict]:
    vault_id = item.get("address") or item.get("id") or item.get("slug")
    if not vault_id:
        return None

    name = item.get("name") or item.get("strategyName") or vault_id
    chain = item.get("chain") or item.get("network") or "Unknown"
    apy_raw = item.get("net_apy") or item.get("netApy") or item.get("apy")
    try:
        apy = float(apy_raw) * (100 if apy_raw and apy_raw <= 1 else 1)
    except (TypeError, ValueError):
        apy = 0.0

    tvl_usd = float(item.get("tvl_usd") or item.get("tvl") or 0.0)
    token_pair = item.get("symbol") or item.get("depositTokenSymbol") or "/".join(item.get("assets", []))

    return {
        "id": f"sommelier:{vault_id}",
        "source": "sommelier",
        "name": name,
        "protocol": "Sommelier",
        "chain": format_chain_name(chain),
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": token_pair,
        "url": item.get("details_url") or item.get("url") or item.get("strategyUrl"),
        "icon_url": _lookup_protocol_icon("Sommelier"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "manager": item.get("manager"),
            "strategy": item.get("strategy"),
        },
    }


def normalize_pendle_yield(item: Dict) -> Optional[Dict]:
    market_id = item.get("market") or item.get("marketAddress") or item.get("id")
    if not market_id:
        return None

    apy = float(item.get("apy") or item.get("total_apy") or 0.0)
    tvl_usd = float(item.get("tvl") or item.get("tvlUsd") or item.get("liquidity") or 0.0)
    chain = item.get("chain") or item.get("network") or "Unknown"
    protocol = "Pendle"
    token_pair = item.get("pair") or item.get("assetSymbol") or item.get("tokens") or ""

    return {
        "id": f"pendle:{market_id}",
        "source": "pendle",
        "name": item.get("name") or item.get("marketName") or market_id,
        "protocol": protocol,
        "chain": format_chain_name(chain),
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": token_pair,
        "url": item.get("url") or item.get("explorerUrl") or f"https://app.pendle.finance/market/{market_id}",
        "icon_url": _lookup_protocol_icon(protocol),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "lp_apy": item.get("lp_apy"),
            "base_apy": item.get("base_apy"),
        },
    }


def normalize_stakedao_vault(item: Dict) -> Optional[Dict]:
    vault_id = item.get("id") or item.get("address") or item.get("slug")
    if not vault_id:
        return None

    apy_raw = item.get("apy") or item.get("apr")
    try:
        apy = float(apy_raw) * (100 if apy_raw and apy_raw <= 1 else 1)
    except (TypeError, ValueError):
        apy = 0.0

    tvl_usd = float(item.get("tvl") or item.get("tvlUsd") or 0.0)
    chain = item.get("chain") or item.get("network") or "Unknown"
    protocol = "StakeDAO"
    token_pair = item.get("symbol") or item.get("underlying") or ""

    return {
        "id": f"stakedao:{vault_id}",
        "source": "stakedao",
        "name": item.get("name") or item.get("displayName") or vault_id,
        "protocol": protocol,
        "chain": format_chain_name(chain),
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": token_pair,
        "url": item.get("url") or item.get("detailsUrl") or item.get("stakingUrl"),
        "icon_url": _lookup_protocol_icon(protocol),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "category": item.get("category"),
        },
    }


def normalize_morpho_market(item: Dict) -> Optional[Dict]:
    market_id = item.get("id")
    if not market_id:
        return None

    apy = float(item.get("supplyApy") or 0.0) * 100
    tvl_usd = float(item.get("totalSupplyUSD") or 0.0)
    chain = item.get("chain") or "Unknown"
    symbol = item.get("underlyingTokenSymbol") or item.get("name") or ""

    return {
        "id": f"morpho:{market_id}",
        "source": "morpho",
        "name": item.get("name") or symbol or market_id,
        "protocol": "Morpho",
        "chain": format_chain_name(chain),
        "apy": apy,
        "tvl_usd": tvl_usd,
        "tvl_growth_24h": 0.0,
        "risk_index": None,
        "ai_score": None,
        "ai_comment": None,
        "token_pair": symbol,
        "url": f"https://app.morpho.org/market/{market_id}",
        "icon_url": _lookup_protocol_icon("Morpho"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "underlying": item.get("underlyingTokenAddress"),
        },
    }


def format_chain_name(chain: str) -> str:
    if not chain:
        return "Unknown"
    normalized = chain.strip()
    replacements = {
        "eth": "Ethereum",
        "ethereum": "Ethereum",
        "arb": "Arbitrum",
        "arbitrum one": "Arbitrum",
        "polygon pos": "Polygon",
    }
    lowered = normalized.lower()
    return replacements.get(lowered, normalized.title())


NORMALIZERS = {
    "defillama": normalize_defillama_pool,
    "beefy": normalize_beefy_vault,
    "yearn": normalize_yearn_vault,
    "sommelier": normalize_sommelier_vault,
    "pendle": normalize_pendle_yield,
    "stakedao": normalize_stakedao_vault,
    "morpho": normalize_morpho_market,
}


def normalize(source: str, records: Iterable[Dict]) -> List[Dict]:
    func = NORMALIZERS.get(source)
    if not func:
        return []
    normalized: List[Dict] = []
    for record in records:
        try:
            data = func(record)
        except Exception:  # pragma: no cover - safety net
            continue
        if data is None:
            continue
        normalized.append(data)
    return normalized
