"""Configuration helpers for the data collector."""

from __future__ import annotations

import os
from typing import Final


DEFILLAMA_YIELDS_URL: Final[str] = os.getenv("DEFILLAMA_URL", "https://yields.llama.fi/pools")
DEFILLAMA_PROTOCOLS_URL: Final[str] = os.getenv("DEFILLAMA_PROTOCOLS_URL", "https://api.llama.fi/protocols")
BEEFY_VAULTS_URL: Final[str] = os.getenv("BEEFY_VAULTS_URL", "https://api.beefy.finance/vaults")
BEEFY_APY_URL: Final[str] = os.getenv("BEEFY_URL", "https://api.beefy.finance/apy")
YEARN_VAULTS_URL: Final[str] = os.getenv("YEARN_URL", "https://api.yearn.finance/v1/chains/1/vaults/all")
SOMMELIER_VAULTS_URL: Final[str] = os.getenv("SOMMELIER_URL", "https://sommelier-api.net/vaults")
PENDLE_YIELD_URL: Final[str] = os.getenv("PENDLE_URL", "https://api.pendle.finance/api/v2/yield")
MORPHO_GRAPHQL_URL: Final[str] = os.getenv("MORPHO_URL", "https://api.morpho.org/graphql")
STAKEDAO_VAULTS_URL: Final[str] = os.getenv("STAKEDAO_URL", "https://stake-dao.api/vaults")

COINGECKO_MARKET_URL: Final[str] = os.getenv("COINGECKO_MARKET_URL", "https://api.coingecko.com/api/v3/coins/markets")
COINGECKO_VS_CURRENCY: Final[str] = os.getenv("COINGECKO_VS_CURRENCY", "usd")
COINGECKO_PER_PAGE: Final[int] = int(os.getenv("COINGECKO_PER_PAGE", "250"))
COINGECKO_PAGES: Final[int] = int(os.getenv("COINGECKO_PAGES", "2"))

REDIS_URL: Final[str] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

DEFAULT_ICON_URL: Final[str] = os.getenv("DEFAULT_PROTOCOL_ICON", "https://icons.llama.fi/icons/unknown.png")

# Redis keys
LATEST_STRATEGIES_KEY: Final[str] = "strategies:latest"
STRATEGY_HISTORY_HASH: Final[str] = "strategies:last"
STRATEGY_ITEM_HASH: Final[str] = "strategies:items"
STRATEGY_TVL_PREFIX: Final[str] = "strategies:tvl"
PROTOCOL_SET_KEY: Final[str] = "strategies:protocols"
CHAIN_SET_KEY: Final[str] = "strategies:chains"

# Timeouts
HTTP_TIMEOUT_SECONDS: Final[int] = int(os.getenv("COLLECTOR_HTTP_TIMEOUT", "30"))
LATEST_TTL_SECONDS: Final[int] = int(os.getenv("STRATEGIES_CACHE_TTL", str(60 * 30)))  # 30 minutes
