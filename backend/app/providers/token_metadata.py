"""Token metadata provider for Aptos tokens"""
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AptosTokenMetadataProvider:
    """Provider for fetching token metadata (symbol, name, decimals) from Aptos"""
    
    def __init__(self):
        self.node_url = settings.APTOS_NODE_URL
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    async def get_token_metadata(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Get token metadata from Aptos node
        
        Args:
            token_address: Token fungible asset address
        
        Returns:
            Dictionary with symbol, name, decimals, or None if not found
        """
        # Check cache first
        cache_key = token_address.lower()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to get from Aptos node
        # Note: Aptos uses fungible asset metadata
        # We'll try to get it from the resource account
        try:
            # For Aptos, we need to query the resource account
            # Format: 0x1::fungible_asset::Metadata
            # But we need the resource account address, not the asset type
            
            # Alternative: Use Dexscreener to get token info
            # Dexscreener has token metadata in their API
            metadata = await self._get_from_dexscreener(token_address)
            
            if metadata:
                self.cache[cache_key] = metadata
                return metadata
            
            # Fallback: Try to parse from known addresses
            metadata = self._get_known_token(token_address)
            if metadata:
                self.cache[cache_key] = metadata
                return metadata
            
        except Exception as e:
            logger.warning(f"Error fetching token metadata for {token_address}: {e}")
        
        return None
    
    async def _get_from_dexscreener(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Try to get token metadata from Dexscreener"""
        try:
            # Dexscreener search by address
            url = f"{settings.DEXSCREENER_API_URL}/latest/dex/tokens/{token_address}"
            response = await self.client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                if pairs:
                    # Get token info from first pair
                    pair = pairs[0]
                    base_token = pair.get("baseToken", {})
                    quote_token = pair.get("quoteToken", {})
                    
                    # Check which token matches
                    if base_token.get("address", "").lower() == token_address.lower():
                        return {
                            "symbol": base_token.get("symbol", ""),
                            "name": base_token.get("name", ""),
                            "decimals": base_token.get("decimals", 8),
                        }
                    elif quote_token.get("address", "").lower() == token_address.lower():
                        return {
                            "symbol": quote_token.get("symbol", ""),
                            "name": quote_token.get("name", ""),
                            "decimals": quote_token.get("decimals", 8),
                        }
        except Exception as e:
            logger.debug(f"Dexscreener lookup failed for {token_address}: {e}")
        
        return None
    
    def _get_known_token(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get metadata for known Aptos tokens"""
        known_tokens = {
            "0x0000000000000000000000000000000000000000000000000000000000000001": {
                "symbol": "APT",
                "name": "Aptos",
                "decimals": 8,
            },
            "0x1": {
                "symbol": "APT",
                "name": "Aptos",
                "decimals": 8,
            },
            "0xa": {
                "symbol": "APT",
                "name": "Aptos",
                "decimals": 8,
            },
            "0x000000000000000000000000000000000000000000000000000000000000000a": {
                "symbol": "APT",
                "name": "Aptos",
                "decimals": 8,
            },
        }
        
        # Normalize address
        normalized = token_address.lower().strip()
        if normalized in known_tokens:
            return known_tokens[normalized]
        
        # Check if it's a short form of APT
        if normalized == "0x1" or normalized == "0xa" or normalized.endswith("000000000000000000000000000000000000000000000000000000000000000a"):
            return known_tokens.get("0x000000000000000000000000000000000000000000000000000000000000000a", known_tokens["0xa"])
        
        return None
    
    async def get_token_symbol(self, token_address: str) -> Optional[str]:
        """Get token symbol only"""
        metadata = await self.get_token_metadata(token_address)
        return metadata.get("symbol") if metadata else None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

