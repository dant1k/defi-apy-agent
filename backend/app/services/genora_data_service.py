"""GenoraDataService - selects and uses appropriate data providers"""
from typing import List, Optional, Dict, Any
from app.providers.base import DexMetricsProvider, PoolMetricsProvider
from app.providers.defillama import DefiLlamaProvider
from app.providers.dexscreener import DexscreenerProvider
from app.providers.aptos_indexer import AptosIndexerProvider
from app.providers.hyperion_api import HyperionApiProvider


class GenoraDataService:
    """Service layer that selects and uses data providers"""
    
    def __init__(self):
        # Level 1: DEX metrics from DefiLlama
        self.dex_provider: DexMetricsProvider = DefiLlamaProvider()
        
        # Level 2: Pools MVP from Dexscreener
        self.pool_provider: PoolMetricsProvider = DexscreenerProvider()
        
        # Level 3: Real fees from Aptos Indexer (optional)
        try:
            self.aptos_indexer_provider = AptosIndexerProvider()
        except Exception as e:
            print(f"Warning: Aptos Indexer provider not available: {e}")
            self.aptos_indexer_provider = None
        
        # Hyperion API: Official API for Hyperion pools
        self.hyperion_api_provider: HyperionApiProvider = HyperionApiProvider()
    
    async def get_dex_list(self, chain: str = "aptos") -> List[Dict[str, Any]]:
        """Get DEX list using DefiLlama provider"""
        return await self.dex_provider.fetch_dex_list_by_chain(chain)
    
    async def get_dex_metrics(
        self, 
        dex_slug: str, 
        dex_name: str = None,
        chain: str = "aptos",
        timeframe: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Get DEX metrics using Level 1: DefiLlama only
        - TVL from /protocol endpoint
        - Fees (24h/7d/30d/cumulative) from /fees endpoint
        """
        # Level 1: DefiLlama for DEX-level metrics
        return await self.dex_provider.fetch_dex_metrics(dex_slug, timeframe)
    
    async def get_dex_charts_30d(self, dex_slug: str) -> List[Dict[str, Any]]:
        """Get 30-day DEX charts using DefiLlama provider"""
        return await self.dex_provider.fetch_dex_charts_30d(dex_slug)
    
    async def get_pools_for_dex(
        self, 
        chain: str = "aptos", 
        dex_slug: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get pools for a DEX
        
        Strategy:
        - If Hyperion: use Hyperion API (best source for Hyperion pools)
        - Otherwise: use Dexscreener provider (Level 2)
        """
        if dex_slug == "hyperion":
            # Use Hyperion API for Hyperion pools
            return await self.hyperion_api_provider.fetch_pools_for_dex(chain, dex_slug)
        else:
            # Use Dexscreener for other DEXes
            return await self.pool_provider.fetch_pools_for_dex(chain, dex_slug)
    
    async def search_pools(
        self, 
        chain: str = "aptos", 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """Search pools using Dexscreener provider"""
        return await self.pool_provider.search_pools(chain, query)
    
    async def get_pool_real_fees(
        self,
        chain: str,
        dex_slug: str,
        pool_address: str,
        token0_address: str,
        token1_address: str,
        token0_decimals: int = 8,
        token1_decimals: int = 8,
        timeframe: str = "24h"
    ) -> Optional[Dict[str, Any]]:
        """
        Level 3: Get real fees for a pool from Aptos Indexer (blockchain events)
        
        Args:
            chain: Blockchain name (e.g., "aptos")
            dex_slug: DEX identifier
            pool_address: Pool contract address
            token0_address: Token0 contract address
            token1_address: Token1 contract address
            token0_decimals: Token0 decimals
            token1_decimals: Token1 decimals
            timeframe: Timeframe for fees ("24h", "7d", "30d")
        
        Returns:
            Dictionary with fees_usd, updated_at, source, or None if not available
        """
        if not self.aptos_indexer_provider or not self.aptos_indexer_provider.enabled:
            return None
        
        return await self.aptos_indexer_provider.get_pool_real_fees(
            chain,
            dex_slug,
            pool_address,
            token0_address,
            token1_address,
            token0_decimals,
            token1_decimals,
            timeframe
        )
    
    async def get_pool_by_id(
        self,
        pool_id: str,
        dex_slug: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get pool by ID
        
        Strategy:
        - If Hyperion: use Hyperion API
        - Otherwise: try Dexscreener or return None
        """
        if dex_slug == "hyperion":
            return await self.hyperion_api_provider.fetch_pool_by_id(pool_id)
        else:
            # Dexscreener doesn't have direct pool by ID, return None
            return None
    
    async def close(self):
        """Close all providers"""
        if hasattr(self.dex_provider, 'close'):
            await self.dex_provider.close()
        if hasattr(self.pool_provider, 'close'):
            await self.pool_provider.close()
        if self.aptos_indexer_provider and hasattr(self.aptos_indexer_provider, 'close'):
            await self.aptos_indexer_provider.close()
        if hasattr(self.hyperion_api_provider, 'close'):
            await self.hyperion_api_provider.close()

