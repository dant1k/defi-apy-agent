"""Price Oracle for converting token amounts to USD"""
import httpx
from typing import Optional, Dict, Any
from decimal import Decimal
from app.core.config import settings


class PriceOracle:
    """Price oracle for token price conversion to USD"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # Cache prices for 60 seconds
    
    async def get_token_price_usd(
        self,
        token_address: str,
        token_symbol: str = None
    ) -> Optional[Decimal]:
        """
        Get token price in USD
        
        Args:
            token_address: Token contract address
            token_symbol: Token symbol (optional, for fallback)
        
        Returns:
            Price in USD or None if not available
        """
        # Check cache first
        cache_key = token_address.lower()
        if cache_key in self.price_cache:
            cached = self.price_cache[cache_key]
            # TODO: Check TTL
            return Decimal(str(cached.get("price", 0)))
        
        # Try DefiLlama first (fastest)
        price = await self._get_price_from_defillama(token_address, token_symbol)
        
        if price is None:
            # Fallback to CoinGecko
            price = await self._get_price_from_coingecko(token_address, token_symbol)
        
        if price:
            self.price_cache[cache_key] = {
                "price": float(price),
                "timestamp": None,  # TODO: Add timestamp for TTL
            }
        
        return price
    
    async def _get_price_from_defillama(
        self,
        token_address: str,
        token_symbol: str = None
    ) -> Optional[Decimal]:
        """Get price from DefiLlama"""
        try:
            # DefiLlama prices endpoint
            # Format: https://coins.llama.fi/prices/current/{chain}:{address}
            url = f"{settings.DEFILLAMA_API_URL}/prices/current/aptos:{token_address}"
            response = await self.client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                coin_key = f"aptos:{token_address.lower()}"
                if coin_key in data.get("coins", {}):
                    price = data["coins"][coin_key].get("price")
                    if price:
                        return Decimal(str(price))
        except Exception as e:
            print(f"Error fetching price from DefiLlama for {token_address}: {e}")
        
        return None
    
    async def _get_price_from_coingecko(
        self,
        token_address: str,
        token_symbol: str = None
    ) -> Optional[Decimal]:
        """Get price from CoinGecko"""
        try:
            # CoinGecko API for Aptos tokens
            # Note: CoinGecko may not have all Aptos tokens
            if token_symbol:
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    "ids": token_symbol.lower(),
                    "vs_currencies": "usd"
                }
                response = await self.client.get(url, params=params, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if token_symbol.lower() in data:
                        price = data[token_symbol.lower()].get("usd")
                        if price:
                            return Decimal(str(price))
        except Exception as e:
            print(f"Error fetching price from CoinGecko for {token_address}: {e}")
        
        return None
    
    async def convert_fees_to_usd(
        self,
        fee_token0: Decimal,
        fee_token1: Decimal,
        token0_address: str,
        token1_address: str,
        token0_decimals: int = 8,
        token1_decimals: int = 8
    ) -> Optional[Decimal]:
        """
        Convert fees from tokens to USD
        
        Args:
            fee_token0: Fee amount in token0 (raw, with decimals)
            fee_token1: Fee amount in token1 (raw, with decimals)
            token0_address: Token0 contract address
            token1_address: Token1 contract address
            token0_decimals: Token0 decimals
            token1_decimals: Token1 decimals
        
        Returns:
            Total fees in USD or None if prices unavailable
        """
        total_usd = Decimal("0")
        prices_available = False
        
        # Convert token0 fees
        if fee_token0 > 0:
            fee_token0_normalized = fee_token0 / Decimal(10 ** token0_decimals)
            price0 = await self.get_token_price_usd(token0_address)
            if price0:
                total_usd += fee_token0_normalized * price0
                prices_available = True
        
        # Convert token1 fees
        if fee_token1 > 0:
            fee_token1_normalized = fee_token1 / Decimal(10 ** token1_decimals)
            price1 = await self.get_token_price_usd(token1_address)
            if price1:
                total_usd += fee_token1_normalized * price1
                prices_available = True
        
        # Return None if no prices available (don't approximate)
        if not prices_available:
            return None
        
        return total_usd
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

