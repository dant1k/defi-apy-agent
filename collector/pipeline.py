"""High-level orchestration for the data collection pipeline."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List

from .data_sources import fetch_coingecko_markets, iter_all_sources
from .normalizer import normalize
from .storage import StrategyStorage, compute_growth

logger = logging.getLogger(__name__)


def _extract_symbols(strategy: Dict) -> List[str]:
    symbols: List[str] = []
    token_pair = strategy.get("token_pair") or ""
    if token_pair:
        for part in token_pair.replace("-", "/").split("/"):
            clean = ''.join(ch for ch in part if ch.isalnum())
            if clean:
                symbols.append(clean.upper())
    return symbols


def _derive_risk_index(strategy: Dict, volatility_map: Dict[str, Dict[str, float]]) -> float:
    apy = float(strategy.get("apy") or 0.0)
    chain = (strategy.get("chain") or "").lower()
    protocol = (strategy.get("protocol") or "").lower()

    symbols = _extract_symbols(strategy)
    vol_samples: List[float] = []
    for symbol in symbols:
        entry = volatility_map.get(symbol)
        if not entry:
            continue
        change_24h = abs(entry.get("price_change_24h", 0.0))
        change_7d = abs(entry.get("price_change_7d", 0.0)) / 2
        vol_samples.append(change_24h + change_7d)

    if vol_samples:
        volatility_score = sum(vol_samples) / len(vol_samples)
    else:
        volatility_score = 15.0  # assume medium volatility when unknown

    base = 1.0 + min(volatility_score / 25, 3.0)

    if apy > 50:
        base += 0.5
    if apy > 120:
        base += 0.5
    if any(keyword in chain for keyword in ("arbitrum", "optimism", "polygon", "base")):
        base += 0.2
    if "stable" in (strategy.get("token_pair") or "").lower():
        base -= 0.3
    if protocol in {"yearn", "aave", "compound", "beefy", "lido"}:
        base -= 0.2
    return max(0.5, min(base, 6.0))


def _compute_ai_score(strategy: Dict) -> float:
    apy = float(strategy.get("apy") or 0.0)
    growth = float(strategy.get("tvl_growth_24h") or 0.0)
    risk = float(strategy.get("risk_index") or 1.0)
    effective_growth = max(growth, 1.0)
    raw_score = (apy * effective_growth) / max(risk, 0.1)
    # Compress into 0-100 range for now.
    score = min(100.0, raw_score)
    return round(score, 2)


def _build_ai_comment(strategy: Dict) -> str:
    apy = round(float(strategy.get("apy") or 0.0), 2)
    growth = round(float(strategy.get("tvl_growth_24h") or 0.0), 2)
    protocol = strategy.get("protocol", "Unknown protocol")
    chain = strategy.get("chain", "Unknown chain")
    risk = round(float(strategy.get("risk_index") or 1.0), 2)
    sentiment = "steady" if growth >= 0 else "declining"
    return (
        f"{protocol} на {chain} показывает APY {apy}% и {sentiment} TVL за 24ч ({growth}%). "
        f"Текущий оценочный риск: {risk}."
    )


def _build_volatility_map() -> Dict[str, Dict[str, float]]:
    markets = fetch_coingecko_markets()
    mapping: Dict[str, Dict[str, float]] = {}
    for item in markets:
        symbol = (item.get("symbol") or "").upper()
        if not symbol:
            continue
        mapping[symbol] = {
            "price_change_24h": float(item.get("price_change_percentage_24h") or item.get("price_change_percentage_24h_in_currency") or 0.0),
            "price_change_7d": float(
                item.get("price_change_percentage_7d")
                or item.get("price_change_percentage_7d_in_currency")
                or 0.0
            ),
        }
    return mapping


def collect_and_store() -> Dict[str, int]:
    storage = StrategyStorage()
    aggregated: Dict[str, Dict] = {}
    now = datetime.now(timezone.utc)
    total_raw = 0
    volatility_map = _build_volatility_map()

    try:
        for source, records in iter_all_sources():
            normalized = normalize(source, records)
            total_raw += len(records)
            logger.info("Fetched %s entries from %s (%s normalized)", len(records), source, len(normalized))
            for item in normalized:
                strategy_id = item["id"]
                # Merge duplicates by preferring higher APY.
                existing = aggregated.get(strategy_id)
                if existing and existing.get("apy", 0.0) >= item.get("apy", 0.0):
                    continue
                aggregated[strategy_id] = item

        strategies: List[Dict] = []
        for strategy_id, strategy in aggregated.items():
            tvl_usd = float(strategy.get("tvl_usd") or 0.0)
            growth, snapshot = compute_growth(storage, strategy_id, tvl_usd, now)
            storage.save_snapshot(strategy_id, snapshot)
            storage.append_tvl_point(strategy_id, now, tvl_usd)

            strategy["tvl_growth_24h"] = round(growth, 4)
            strategy["risk_index"] = round(_derive_risk_index(strategy, volatility_map), 4)
            strategy["score"] = round((strategy["apy"] * max(growth, 1.0)) / max(strategy["risk_index"], 0.1), 4)
            strategy["ai_score"] = _compute_ai_score(strategy)
            strategy["ai_comment"] = _build_ai_comment(strategy)
            strategies.append(strategy)

        storage.save_latest(strategies)

        logger.info("Stored %s strategies (%s raw records)", len(strategies), total_raw)
        return {"raw_records": total_raw, "strategies": len(strategies)}
    finally:
        storage.close()
