"""Dexscreener provider implementation"""
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from decimal import Decimal
from app.providers.base import PoolMetricsProvider
from app.core.config import settings


class DexscreenerProvider(PoolMetricsProvider):
    """Dexscreener API provider for Pool metrics"""
    
    def __init__(self):
        self.base_url = settings.DEXSCREENER_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.last_request_time = 0.0
        self.max_retries = 2
    
    async def _rate_limit(self):
        """Rate limit guard"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _request_with_retry(self, url: str) -> Optional[Dict[str, Any]]:
        """Make request with retry logic"""
        await self._rate_limit()
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                print(f"Error fetching from Dexscreener after {self.max_retries + 1} attempts: {e}")
                return None
        
        return None
    
    async def fetch_pools_for_dex(
        self, 
        chain: str = "aptos", 
        dex_slug: str = None
    ) -> List[Dict[str, Any]]:
        """Fetch pools for a specific DEX from Dexscreener"""
        try:
            # Dexscreener doesn't have direct DEX filtering, so we search by chain
            url = f"{self.base_url}/latest/dex/search?q={chain}"
            data = await self._request_with_retry(url)
            
            if not data or not isinstance(data, dict):
                return []
            
            pairs = data.get("pairs", [])
            pools = []
            
            for pair in pairs:
                if pair.get("chainId", "").lower() == chain.lower():
                    # Extract pool data
                    pool_id = pair.get("pairAddress", "")
                    if not pool_id:
                        continue
                    
                    token0 = pair.get("baseToken", {})
                    token1 = pair.get("quoteToken", {})
                    
                    # Calculate TVL, volume, fees
                    liquidity_usd = pair.get("liquidity", {}).get("usd", 0)
                    volume_24h = pair.get("volume", {}).get("h24", 0)
                    fees_24h = pair.get("fees", {}).get("h24", 0) if pair.get("fees") else None
                    
                    pools.append({
                        "id": pool_id,
                        "dex_slug": dex_slug or "unknown",
                        "chain": chain,
                        "token0_address": token0.get("address", ""),
                        "token0_symbol": token0.get("symbol", ""),
                        "token1_address": token1.get("address", ""),
                        "token1_symbol": token1.get("symbol", ""),
                        "address": pool_id,
                        "url": pair.get("url", ""),
                        "tvl_usd": float(Decimal(str(liquidity_usd))),
                        "volume_24h_usd": float(Decimal(str(volume_24h))),
                        "fees_24h_usd": float(Decimal(str(fees_24h))) if fees_24h is not None else None,
                    })
            
            return pools
        except Exception as e:
            print(f"Error fetching pools from Dexscreener: {e}")
            return []
    
    async def search_pools(
        self, 
        chain: str = "aptos", 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """Search pools by query"""
        try:
            if not query:
                return await self.fetch_pools_for_dex(chain)
            
            url = f"{self.base_url}/latest/dex/search?q={query}"
            data = await self._request_with_retry(url)
            
            if not data or not isinstance(data, dict):
                return []
            
            pairs = data.get("pairs", [])
            pools = []
            
            for pair in pairs:
                if pair.get("chainId", "").lower() == chain.lower():
                    pool_id = pair.get("pairAddress", "")
                    if not pool_id:
                        continue
                    
                    token0 = pair.get("baseToken", {})
                    token1 = pair.get("quoteToken", {})
                    
                    liquidity_usd = pair.get("liquidity", {}).get("usd", 0)
                    volume_24h = pair.get("volume", {}).get("h24", 0)
                    fees_24h = pair.get("fees", {}).get("h24", 0) if pair.get("fees") else None
                    
                    pools.append({
                        "id": pool_id,
                        "dex_slug": "unknown",
                        "chain": chain,
                        "token0_address": token0.get("address", ""),
                        "token0_symbol": token0.get("symbol", ""),
                        "token1_address": token1.get("address", ""),
                        "token1_symbol": token1.get("symbol", ""),
                        "address": pool_id,
                        "url": pair.get("url", ""),
                        "tvl_usd": float(Decimal(str(liquidity_usd))),
                        "volume_24h_usd": float(Decimal(str(volume_24h))),
                        "fees_24h_usd": float(Decimal(str(fees_24h))) if fees_24h is not None else None,
                    })
            
            return pools
        except Exception as e:
            print(f"Error searching pools from Dexscreener: {e}")
            return []
    
    # Level 2 (MVP): Dexscreener is only used for pools, not DEX-level aggregation
    # fetch_pools_for_dex already handles fees correctly: returns fees if available, None otherwise
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

