"""Hyperion API provider implementation"""
import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from app.providers.base import PoolMetricsProvider
from app.providers.token_metadata import AptosTokenMetadataProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class HyperionApiProvider(PoolMetricsProvider):
    """Hyperion GraphQL API provider for pool metrics"""
    
    def __init__(self):
        self.base_url = settings.HYPERION_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token_metadata = AptosTokenMetadataProvider()
    
    async def _graphql_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Execute GraphQL query against Hyperion API"""
        try:
            response = await self.client.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL errors from Hyperion API: {data['errors']}")
                return None
            
            return data.get("data")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching from Hyperion API: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error fetching from Hyperion API: {e}")
            return None
    
    async def fetch_pools_for_dex(
        self,
        chain: str = "aptos",
        dex_slug: str = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch pools from Hyperion API
        
        Note: Hyperion API returns all pools when poolId is not provided
        """
        try:
            # Get all pools (no poolId parameter = all pools)
            query = """
            query GetHyperionPools {
                api {
                    getPoolStat {
                        id
                        dailyVolumeUSD
                        feesUSD
                        tvlUSD
                        feeAPR
                        farmAPR
                        pool {
                            token1
                            token2
                            feeRate
                            currentTick
                            sqrtPrice
                        }
                    }
                }
            }
            """
            
            data = await self._graphql_query(query)
            if not data:
                return []
            
            pools_data = data.get("api", {}).get("getPoolStat", [])
            if not isinstance(pools_data, list):
                return []
            
            pools = []
            for pool_stat in pools_data:
                pool_info = pool_stat.get("pool", {})
                pool_id = pool_stat.get("id", "")
                
                if not pool_id:
                    continue
                
                token0_address = pool_info.get("token1", "")  # Note: Hyperion uses token1/token2
                token1_address = pool_info.get("token2", "")
                
                # Get token metadata (symbol, name, decimals)
                token0_symbol = None
                token0_name = None
                token1_symbol = None
                token1_name = None
                
                if token0_address:
                    try:
                        token0_meta = await self.token_metadata.get_token_metadata(token0_address)
                        if token0_meta:
                            token0_symbol = token0_meta.get("symbol")
                            token0_name = token0_meta.get("name")
                    except Exception as e:
                        logger.debug(f"Could not get metadata for token0 {token0_address}: {e}")
                
                if token1_address:
                    try:
                        token1_meta = await self.token_metadata.get_token_metadata(token1_address)
                        if token1_meta:
                            token1_symbol = token1_meta.get("symbol")
                            token1_name = token1_meta.get("name")
                    except Exception as e:
                        logger.debug(f"Could not get metadata for token1 {token1_address}: {e}")
                
                pools.append({
                    "id": pool_id,
                    "dex_slug": "hyperion",
                    "chain": chain,
                    "token0_address": token0_address,
                    "token0_symbol": token0_symbol,
                    "token0_name": token0_name,
                    "token1_address": token1_address,
                    "token1_symbol": token1_symbol,
                    "token1_name": token1_name,
                    "address": pool_id,  # Pool ID is the address
                    "tvl_usd": float(Decimal(str(pool_stat.get("tvlUSD", 0)))),
                    "volume_24h_usd": float(Decimal(str(pool_stat.get("dailyVolumeUSD", 0)))),
                    "fees_24h_usd": float(Decimal(str(pool_stat.get("feesUSD", 0)))) if pool_stat.get("feesUSD") else None,
                    "fee_apr": float(Decimal(str(pool_stat.get("feeAPR", 0)))) if pool_stat.get("feeAPR") else None,
                    "farm_apr": float(Decimal(str(pool_stat.get("farmAPR", 0)))) if pool_stat.get("farmAPR") else None,
                })
            
            # Fetch token symbols in batch (to avoid too many requests)
            # We'll fetch symbols for pools with significant TVL/volume first
            pools_with_activity = [p for p in pools if (p.get("tvl_usd", 0) or 0) > 100 or (p.get("volume_24h_usd", 0) or 0) > 0]
            other_pools = [p for p in pools if p not in pools_with_activity]
            
            # Process active pools first
            for pool in pools_with_activity[:50]:  # Limit to 50 to avoid rate limits
                if pool.get("token0_address"):
                    token0_metadata = await self.token_metadata.get_token_metadata(pool["token0_address"])
                    if token0_metadata:
                        pool["token0_symbol"] = token0_metadata.get("symbol")
                
                if pool.get("token1_address"):
                    token1_metadata = await self.token_metadata.get_token_metadata(pool["token1_address"])
                    if token1_metadata:
                        pool["token1_symbol"] = token1_metadata.get("symbol")
            
            return pools
        except Exception as e:
            logger.error(f"Error fetching pools from Hyperion API: {e}")
            return []
    
    async def fetch_pool_by_id(self, pool_id: str) -> Optional[Dict[str, Any]]:
        """Fetch specific pool by ID from Hyperion API"""
        try:
            query = """
            query GetHyperionPool($poolId: String!) {
                api {
                    getPoolStat(poolId: $poolId) {
                        id
                        dailyVolumeUSD
                        feesUSD
                        tvlUSD
                        feeAPR
                        farmAPR
                        pool {
                            token1
                            token2
                            feeRate
                            currentTick
                            sqrtPrice
                            activeLpAmount
                        }
                    }
                }
            }
            """
            
            variables = {"poolId": pool_id}
            data = await self._graphql_query(query, variables)
            
            if not data:
                return None
            
            pools_data = data.get("api", {}).get("getPoolStat", [])
            if not pools_data or len(pools_data) == 0:
                return None
            
            pool_stat = pools_data[0]
            pool_info = pool_stat.get("pool", {})
            
            token0_address = pool_info.get("token1", "")
            token1_address = pool_info.get("token2", "")
            
            # Get token symbols
            token0_symbol = None
            token1_symbol = None
            
            if token0_address:
                token0_metadata = await self.token_metadata.get_token_metadata(token0_address)
                if token0_metadata:
                    token0_symbol = token0_metadata.get("symbol")
            
            if token1_address:
                token1_metadata = await self.token_metadata.get_token_metadata(token1_address)
                if token1_metadata:
                    token1_symbol = token1_metadata.get("symbol")
            
            return {
                "id": pool_stat.get("id", pool_id),
                "dex_slug": "hyperion",
                "chain": "aptos",
                "token0_address": token0_address,
                "token0_symbol": token0_symbol,
                "token1_address": token1_address,
                "token1_symbol": token1_symbol,
                "address": pool_stat.get("id", pool_id),
                "tvl_usd": float(Decimal(str(pool_stat.get("tvlUSD", 0)))),
                "volume_24h_usd": float(Decimal(str(pool_stat.get("dailyVolumeUSD", 0)))),
                "fees_24h_usd": float(Decimal(str(pool_stat.get("feesUSD", 0)))) if pool_stat.get("feesUSD") else None,
                "fee_apr": float(Decimal(str(pool_stat.get("feeAPR", 0)))) if pool_stat.get("feeAPR") else None,
                "farm_apr": float(Decimal(str(pool_stat.get("farmAPR", 0)))) if pool_stat.get("farmAPR") else None,
                "fee_rate": pool_info.get("feeRate"),  # feeRate: 100 = 0.01%
                "current_tick": pool_info.get("currentTick"),
                "sqrt_price": pool_info.get("sqrtPrice"),
                "active_lp_amount": pool_info.get("activeLpAmount"),
            }
        except Exception as e:
            logger.error(f"Error fetching pool {pool_id} from Hyperion API: {e}")
            return None
    
    async def search_pools(
        self,
        chain: str = "aptos",
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """Search pools - Hyperion API doesn't support search, return all pools"""
        # Hyperion API doesn't have search, so return all pools
        return await self.fetch_pools_for_dex(chain, None)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

