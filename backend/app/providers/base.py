"""Base provider interfaces"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime


class DexMetricsProvider(ABC):
    """Abstract base class for DEX metrics providers"""
    
    @abstractmethod
    async def fetch_dex_list_by_chain(self, chain: str = "aptos") -> List[Dict[str, Any]]:
        """
        Fetch list of DEXes for a given chain
        
        Returns:
            List of DEX dictionaries with keys: slug, name, chain, url, logo_url
        """
        pass
    
    @abstractmethod
    async def fetch_dex_metrics(
        self, 
        dex_slug: str, 
        timeframe: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch metrics for a specific DEX
        
        Args:
            dex_slug: DEX identifier
            timeframe: Timeframe for metrics (e.g., "1d", "7d", "30d")
        
        Returns:
            Dictionary with metrics: tvl_usd, volume_24h_usd, fees_24h_usd, etc.
        """
        pass
    
    @abstractmethod
    async def fetch_dex_charts_30d(self, dex_slug: str) -> List[Dict[str, Any]]:
        """
        Fetch 30-day chart data for a DEX
        
        Args:
            dex_slug: DEX identifier
        
        Returns:
            List of data points with timestamp and metrics
        """
        pass


class PoolMetricsProvider(ABC):
    """Abstract base class for Pool metrics providers"""
    
    @abstractmethod
    async def fetch_pools_for_dex(
        self, 
        chain: str = "aptos", 
        dex_slug: str = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch pools for a specific DEX
        
        Args:
            chain: Blockchain name
            dex_slug: DEX identifier (optional)
        
        Returns:
            List of pool dictionaries with keys: id, token0, token1, tvl, volume, fees, address
        """
        pass
    
    @abstractmethod
    async def search_pools(
        self, 
        chain: str = "aptos", 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search pools by query
        
        Args:
            chain: Blockchain name
            query: Search query (token symbol, address, etc.)
        
        Returns:
            List of matching pools
        """
        pass

