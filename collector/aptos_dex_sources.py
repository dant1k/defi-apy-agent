"""Источники данных для Aptos DEX метрик.

Временный источник с моками.
TODO: заменить на реальные запросы к внешним API Aptos DEX
"""

from __future__ import annotations

from typing import Dict, List


def fetch_aptos_dexes() -> Dict[str, List]:
    """
    Возвращает словарь с двумя списками.

    {
      "dexes": [...],   # список DEX агрегатов
      "pools": [...]    # список пулов
    }

    Все числа во float, суммы в USD
    """
    dexes = [
        {
            "name": "Thala",
            "slug": "thala",
            "chain": "aptos",
            "tvl_usd": 3862624.02,
            "volume": {
                "24h": 1200000.0,
                "7d": 7800000.0,
                "30d": 31000000.0,
                "all": 55000000.0,
            },
            "fees": {
                "24h": 8500.0,
                "7d": 56000.0,
                "30d": 230000.0,
                "all": 410000.0,
            },
        },
    ]

    pools = [
        {
            "id": "thala-apt-usdc-005",
            "dex_slug": "thala",
            "address": "0xPOOL_ADDRESS",
            "token0": "APT",
            "token1": "USDC",
            "pair": "APT-USDC",
            "fee_tier": 0.05,
            "tvl_usd": 3390000.0,
            "volume": {
                "24h": 3440000.0,
                "7d": 15000000.0,
                "30d": 42000000.0,
                "all": 80000000.0,
            },
            "fees": {
                "24h": 1720.0,
                "7d": 9000.0,
                "30d": 31000.0,
                "all": 60000.0,
            },
            # APR считаем из fees_7d
            "apr_fee": 0.0,  # временно, пересчитаем дальше
        },
    ]

    # Пересчитать apr_fee как годовой из fees_7d
    for p in pools:
        tvl = p["tvl_usd"] or 1.0
        weekly_fees = p["fees"]["7d"]
        p["apr_fee"] = (weekly_fees * 52) / tvl

    return {"dexes": dexes, "pools": pools}

