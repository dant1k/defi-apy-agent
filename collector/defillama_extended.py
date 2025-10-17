#!/usr/bin/env python3
"""
Extended DeFiLlama Integration for Genora
Advanced data collection and analysis from DeFiLlama API
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeFiLlamaExtended:
    """Extended DeFiLlama API client with advanced features"""
    
    def __init__(self):
        self.base_url = "https://api.llama.fi"
        self.session = None
        self.rate_limit_delay = 0.1  # 100ms between requests
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make rate-limited request to DeFiLlama API"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            await asyncio.sleep(self.rate_limit_delay)
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return {}
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {}
    
    async def get_all_protocols(self) -> List[Dict[str, Any]]:
        """Get all protocols with extended data"""
        try:
            protocols = await self._make_request("protocols")
            
            # Enhance protocol data
            enhanced_protocols = []
            for protocol in protocols:
                enhanced = {
                    "id": protocol.get("id", ""),
                    "name": protocol.get("name", ""),
                    "symbol": protocol.get("symbol", ""),
                    "url": protocol.get("url", ""),
                    "description": protocol.get("description", ""),
                    "logo": protocol.get("logo", ""),
                    "chains": protocol.get("chains", []),
                    "tvl": protocol.get("tvl", 0),
                    "tvl_change_24h": protocol.get("change_1d", 0),
                    "tvl_change_7d": protocol.get("change_7d", 0),
                    "tvl_change_30d": protocol.get("change_30d", 0),
                    "category": protocol.get("category", "unknown"),
                    "parent_protocol": protocol.get("parentProtocol", ""),
                    "listed_at": protocol.get("listedAt", 0),
                    "gecko_id": protocol.get("gecko_id", ""),
                    "cmc_id": protocol.get("cmcId", ""),
                    "twitter": protocol.get("twitter", ""),
                    "github": protocol.get("github", ""),
                    "audit_links": protocol.get("audit_links", []),
                    "oracles": protocol.get("oracles", []),
                    "forks": protocol.get("forks", []),
                    "hallmarks": protocol.get("hallmarks", []),
                    "deadline": protocol.get("deadline", 0),
                    "mcap": protocol.get("mcap", 0),
                    "fdv": protocol.get("fdv", 0),
                    "token_price": protocol.get("tokenPrice", 0),
                    "token_supply": protocol.get("tokenSupply", 0),
                    "tokens": protocol.get("tokens", []),
                    "tokens_in_usd": protocol.get("tokensInUsd", []),
                    "tokens_tvl": protocol.get("tokensTvl", []),
                    "staking": protocol.get("staking", {}),
                    "pool2": protocol.get("pool2", {}),
                    "borrowed": protocol.get("borrowed", {}),
                    "doublecounted": protocol.get("doublecounted", False),
                    "liquidstaking": protocol.get("liquidstaking", False),
                    "yield_aggregator": protocol.get("yield_aggregator", False),
                    "insurance": protocol.get("insurance", False),
                    "analytics": protocol.get("analytics", {}),
                    "metrics": protocol.get("metrics", {}),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_protocols.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_protocols)} protocols")
            return enhanced_protocols
            
        except Exception as e:
            logger.error(f"Failed to get protocols: {e}")
            return []
    
    async def get_protocol_details(self, protocol_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific protocol"""
        try:
            # Get protocol TVL history
            tvl_history = await self._make_request(f"protocol/{protocol_id}")
            
            # Get protocol token data
            token_data = await self._make_request(f"protocol/{protocol_id}/tokens")
            
            # Get protocol fees and revenue
            fees_data = await self._make_request(f"protocol/{protocol_id}/fees")
            
            # Get protocol revenue
            revenue_data = await self._make_request(f"protocol/{protocol_id}/revenue")
            
            # Combine all data
            protocol_details = {
                "id": protocol_id,
                "tvl_history": tvl_history,
                "token_data": token_data,
                "fees_data": fees_data,
                "revenue_data": revenue_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return protocol_details
            
        except Exception as e:
            logger.error(f"Failed to get protocol details for {protocol_id}: {e}")
            return {}
    
    async def get_chain_tvl(self) -> List[Dict[str, Any]]:
        """Get TVL data for all chains"""
        try:
            chains_data = await self._make_request("chains")
            
            enhanced_chains = []
            for chain in chains_data:
                enhanced = {
                    "name": chain.get("name", ""),
                    "tokenSymbol": chain.get("tokenSymbol", ""),
                    "cmcId": chain.get("cmcId", ""),
                    "gecko_id": chain.get("gecko_id", ""),
                    "tvl": chain.get("tvl", 0),
                    "tvl_change_24h": chain.get("change_1d", 0),
                    "tvl_change_7d": chain.get("change_7d", 0),
                    "tvl_change_30d": chain.get("change_30d", 0),
                    "tokenPrice": chain.get("tokenPrice", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_chains.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_chains)} chains")
            return enhanced_chains
            
        except Exception as e:
            logger.error(f"Failed to get chains data: {e}")
            return []
    
    async def get_chain_tvl_history(self, chain: str) -> List[Dict[str, Any]]:
        """Get historical TVL data for a specific chain"""
        try:
            history = await self._make_request(f"v2/historicalChainTvl/{chain}")
            
            enhanced_history = []
            for entry in history:
                enhanced = {
                    "date": entry.get("date", 0),
                    "tvl": entry.get("tvl", 0),
                    "tokens": entry.get("tokens", {}),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_history.append(enhanced)
            
            return enhanced_history
            
        except Exception as e:
            logger.error(f"Failed to get chain history for {chain}: {e}")
            return []
    
    async def get_treasury_data(self) -> List[Dict[str, Any]]:
        """Get treasury data for protocols"""
        try:
            treasury_data = await self._make_request("treasuries")
            
            enhanced_treasuries = []
            for treasury in treasury_data:
                enhanced = {
                    "name": treasury.get("name", ""),
                    "tvl": treasury.get("tvl", 0),
                    "tokens": treasury.get("tokens", []),
                    "tokens_in_usd": treasury.get("tokensInUsd", []),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_treasuries.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_treasuries)} treasuries")
            return enhanced_treasuries
            
        except Exception as e:
            logger.error(f"Failed to get treasury data: {e}")
            return []
    
    async def get_stablecoins_data(self) -> List[Dict[str, Any]]:
        """Get stablecoin data"""
        try:
            stablecoins = await self._make_request("stablecoins")
            
            enhanced_stablecoins = []
            for stablecoin in stablecoins:
                enhanced = {
                    "id": stablecoin.get("id", ""),
                    "name": stablecoin.get("name", ""),
                    "symbol": stablecoin.get("symbol", ""),
                    "peggedAsset": stablecoin.get("peggedAsset", ""),
                    "peggedUSD": stablecoin.get("peggedUSD", 0),
                    "circulating": stablecoin.get("circulating", {}),
                    "circulatingPrevDay": stablecoin.get("circulatingPrevDay", {}),
                    "circulatingPrevWeek": stablecoin.get("circulatingPrevWeek", {}),
                    "circulatingPrevMonth": stablecoin.get("circulatingPrevMonth", {}),
                    "priceSource": stablecoin.get("priceSource", ""),
                    "chains": stablecoin.get("chains", []),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_stablecoins.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_stablecoins)} stablecoins")
            return enhanced_stablecoins
            
        except Exception as e:
            logger.error(f"Failed to get stablecoins data: {e}")
            return []
    
    async def get_bridges_data(self) -> List[Dict[str, Any]]:
        """Get bridge data"""
        try:
            bridges = await self._make_request("bridges")
            
            enhanced_bridges = []
            for bridge in bridges:
                enhanced = {
                    "name": bridge.get("name", ""),
                    "displayName": bridge.get("displayName", ""),
                    "chains": bridge.get("chains", []),
                    "tvl": bridge.get("tvl", 0),
                    "tvl_change_24h": bridge.get("change_1d", 0),
                    "tvl_change_7d": bridge.get("change_7d", 0),
                    "tvl_change_30d": bridge.get("change_30d", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_bridges.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_bridges)} bridges")
            return enhanced_bridges
            
        except Exception as e:
            logger.error(f"Failed to get bridges data: {e}")
            return []
    
    async def get_raises_data(self) -> List[Dict[str, Any]]:
        """Get funding raises data"""
        try:
            raises = await self._make_request("raises")
            
            enhanced_raises = []
            for raise_data in raises:
                enhanced = {
                    "name": raise_data.get("name", ""),
                    "date": raise_data.get("date", 0),
                    "amount": raise_data.get("amount", 0),
                    "round": raise_data.get("round", ""),
                    "sector": raise_data.get("sector", ""),
                    "source": raise_data.get("source", ""),
                    "description": raise_data.get("description", ""),
                    "leadInvestors": raise_data.get("leadInvestors", []),
                    "otherInvestors": raise_data.get("otherInvestors", []),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_raises.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_raises)} raises")
            return enhanced_raises
            
        except Exception as e:
            logger.error(f"Failed to get raises data: {e}")
            return []
    
    async def get_airdrops_data(self) -> List[Dict[str, Any]]:
        """Get airdrop data"""
        try:
            airdrops = await self._make_request("airdrops")
            
            enhanced_airdrops = []
            for airdrop in airdrops:
                enhanced = {
                    "name": airdrop.get("name", ""),
                    "date": airdrop.get("date", 0),
                    "amount": airdrop.get("amount", 0),
                    "token": airdrop.get("token", ""),
                    "description": airdrop.get("description", ""),
                    "source": airdrop.get("source", ""),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_airdrops.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_airdrops)} airdrops")
            return enhanced_airdrops
            
        except Exception as e:
            logger.error(f"Failed to get airdrops data: {e}")
            return []
    
    async def get_volume_data(self) -> List[Dict[str, Any]]:
        """Get volume data for protocols"""
        try:
            volume_data = await self._make_request("volume")
            
            enhanced_volume = []
            for volume in volume_data:
                enhanced = {
                    "id": volume.get("id", ""),
                    "name": volume.get("name", ""),
                    "volume_24h": volume.get("volume_24h", 0),
                    "volume_7d": volume.get("volume_7d", 0),
                    "volume_30d": volume.get("volume_30d", 0),
                    "volume_change_24h": volume.get("change_24h", 0),
                    "volume_change_7d": volume.get("change_7d", 0),
                    "volume_change_30d": volume.get("change_30d", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_volume.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_volume)} volume records")
            return enhanced_volume
            
        except Exception as e:
            logger.error(f"Failed to get volume data: {e}")
            return []
    
    async def get_fees_data(self) -> List[Dict[str, Any]]:
        """Get fees data for protocols"""
        try:
            fees_data = await self._make_request("fees")
            
            enhanced_fees = []
            for fees in fees_data:
                enhanced = {
                    "id": fees.get("id", ""),
                    "name": fees.get("name", ""),
                    "fees_24h": fees.get("fees_24h", 0),
                    "fees_7d": fees.get("fees_7d", 0),
                    "fees_30d": fees.get("fees_30d", 0),
                    "fees_change_24h": fees.get("change_24h", 0),
                    "fees_change_7d": fees.get("change_7d", 0),
                    "fees_change_30d": fees.get("change_30d", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_fees.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_fees)} fees records")
            return enhanced_fees
            
        except Exception as e:
            logger.error(f"Failed to get fees data: {e}")
            return []
    
    async def get_revenue_data(self) -> List[Dict[str, Any]]:
        """Get revenue data for protocols"""
        try:
            revenue_data = await self._make_request("revenue")
            
            enhanced_revenue = []
            for revenue in revenue_data:
                enhanced = {
                    "id": revenue.get("id", ""),
                    "name": revenue.get("name", ""),
                    "revenue_24h": revenue.get("revenue_24h", 0),
                    "revenue_7d": revenue.get("revenue_7d", 0),
                    "revenue_30d": revenue.get("revenue_30d", 0),
                    "revenue_change_24h": revenue.get("change_24h", 0),
                    "revenue_change_7d": revenue.get("change_7d", 0),
                    "revenue_change_30d": revenue.get("change_30d", 0),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                enhanced_revenue.append(enhanced)
            
            logger.info(f"Retrieved {len(enhanced_revenue)} revenue records")
            return enhanced_revenue
            
        except Exception as e:
            logger.error(f"Failed to get revenue data: {e}")
            return []
    
    async def get_all_extended_data(self) -> Dict[str, Any]:
        """Get all available extended data from DeFiLlama"""
        try:
            logger.info("Starting comprehensive data collection from DeFiLlama...")
            
            # Collect all data types
            data = {
                "protocols": await self.get_all_protocols(),
                "chains": await self.get_chain_tvl(),
                "treasuries": await self.get_treasury_data(),
                "stablecoins": await self.get_stablecoins_data(),
                "bridges": await self.get_bridges_data(),
                "raises": await self.get_raises_data(),
                "airdrops": await self.get_airdrops_data(),
                "volume": await self.get_volume_data(),
                "fees": await self.get_fees_data(),
                "revenue": await self.get_revenue_data(),
                "collected_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Calculate summary statistics
            data["summary"] = {
                "total_protocols": len(data["protocols"]),
                "total_chains": len(data["chains"]),
                "total_treasuries": len(data["treasuries"]),
                "total_stablecoins": len(data["stablecoins"]),
                "total_bridges": len(data["bridges"]),
                "total_raises": len(data["raises"]),
                "total_airdrops": len(data["airdrops"]),
                "total_volume_records": len(data["volume"]),
                "total_fees_records": len(data["fees"]),
                "total_revenue_records": len(data["revenue"]),
                "total_tvl": sum(p.get("tvl", 0) for p in data["protocols"]),
                "total_chain_tvl": sum(c.get("tvl", 0) for c in data["chains"])
            }
            
            logger.info(f"Collected comprehensive data: {data['summary']}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to collect extended data: {e}")
            return {}

# Example usage and testing
async def main():
    """Test the extended DeFiLlama integration"""
    async with DeFiLlamaExtended() as client:
        # Test individual endpoints
        print("Testing DeFiLlama Extended Integration...")
        
        # Get protocols
        protocols = await client.get_all_protocols()
        print(f"Retrieved {len(protocols)} protocols")
        
        # Get chains
        chains = await client.get_chain_tvl()
        print(f"Retrieved {len(chains)} chains")
        
        # Get comprehensive data
        all_data = await client.get_all_extended_data()
        print(f"Comprehensive data summary: {all_data.get('summary', {})}")

if __name__ == "__main__":
    asyncio.run(main())
