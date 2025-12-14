"""Aptos Indexer GraphQL provider implementation for Level 3: Real fees from blockchain events"""
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from app.providers.base import PoolMetricsProvider
from app.providers.adapters import get_adapter
from app.providers.price_oracle import PriceOracle
from app.core.config import settings


class AptosIndexerProvider(PoolMetricsProvider):
    """
    Level 3: Aptos Indexer GraphQL provider
    Fetches real fees from swap events in the blockchain
    """
    
    def __init__(self):
        # Aptos Indexer GraphQL endpoint (from official docs)
        self.base_url = settings.APTOS_INDEXER_URL
        self.client = httpx.AsyncClient(timeout=60.0)
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.last_request_time = 0.0
        self.enabled = bool(self.base_url)
        self.price_oracle = PriceOracle()
    
    async def _rate_limit(self):
        """Rate limit guard"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _graphql_query(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Execute GraphQL query"""
        await self._rate_limit()
        
        try:
            response = await self.client.post(
                self.base_url,
                json={"query": query, "variables": variables or {}},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                return None
            
            return data.get("data")
        except Exception as e:
            print(f"Error executing GraphQL query: {e}")
            return None
    
    async def verify_connection(self) -> bool:
        """
        Verify that Aptos Indexer is accessible and schema matches
        
        Returns:
            True if connection is valid, False otherwise
        """
        query = """
        query VerifyConnection {
            user_transactions(limit: 1) {
                version
            }
        }
        """
        
        try:
            data = await self._graphql_query(query)
            if data and "user_transactions" in data:
                # Connection is valid if we can query user_transactions
                return True
        except Exception as e:
            print(f"Error verifying Aptos Indexer connection: {e}")
        
        return False
    
    async def fetch_fungible_asset_activities_for_transaction(
        self,
        transaction_version: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch fungible asset activities for a transaction (recommended method)
        
        Args:
            transaction_version: Transaction version number
        
        Returns:
            List of fungible asset activities
        """
        query = """
        query FeesDiscovery($v: bigint!) {
            fungible_asset_activities(
                where: { transaction_version: { _eq: $v } }
                order_by: { event_index: asc }
            ) {
                event_index
                owner_address
                asset_type
                type
                amount
                transaction_version
            }
        }
        """
        
        variables = {"v": transaction_version}
        data = await self._graphql_query(query, variables)
        
        if not data:
            return []
        
        return data.get("fungible_asset_activities", [])
    
    async def fetch_swap_transactions_for_pool(
        self,
        pool_address: str,
        entry_functions: List[str],
        start_time: datetime,
        end_time: datetime,
        limit: int = 100
    ) -> List[int]:
        """
        Fetch swap transaction versions for a pool
        
        Args:
            pool_address: Pool contract address
            entry_functions: List of entry function identifiers (e.g., ["0x1::dex::swap"])
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of transactions to fetch
        
        Returns:
            List of transaction versions
        """
        # Query user_transactions filtered by entry function and sender/receiver
        query = """
        query GetSwapTransactions($poolAddress: String!, $entryFunctions: [String!]!, $startTime: timestamp!, $endTime: timestamp!, $limit: Int!) {
            user_transactions(
                where: {
                    entry_function_id_str: {_in: $entryFunctions}
                    _or: [
                        {sender: {_eq: $poolAddress}}
                        {account: {_eq: $poolAddress}}
                    ]
                    transaction_timestamp: {_gte: $startTime, _lte: $endTime}
                }
                order_by: {transaction_timestamp: desc}
                limit: $limit
            ) {
                version
                transaction_timestamp
            }
        }
        """
        
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())
        
        variables = {
            "poolAddress": pool_address,
            "entryFunctions": entry_functions,
            "startTime": start_timestamp,
            "endTime": end_timestamp,
            "limit": limit
        }
        
        data = await self._graphql_query(query, variables)
        if not data:
            return []
        
        transactions = data.get("user_transactions", [])
        return [tx["version"] for tx in transactions]
    
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
        Get real fees for a pool from blockchain events (Level 3)
        Uses fungible_asset_activities for fee discovery
        
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
            Dictionary with:
                - fees_usd: Decimal or None (if prices unavailable)
                - updated_at: ISO timestamp
                - source: "aptos_indexer"
            Or None if adapter not found or errors occur
        """
        try:
            # Get adapter for this DEX
            adapter = get_adapter(dex_slug)
            if not adapter:
                # No adapter for this DEX - return None
                return None
            
            # Calculate time range
            end_time = datetime.utcnow()
            if timeframe == "24h":
                start_time = end_time - timedelta(hours=24)
            elif timeframe == "7d":
                start_time = end_time - timedelta(days=7)
            elif timeframe == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=24)
            
            # Get entry functions for this DEX
            entry_functions = adapter.get_swap_entry_functions()
            
            # Fetch swap transaction versions
            tx_versions = await self.fetch_swap_transactions_for_pool(
                pool_address,
                entry_functions,
                start_time,
                end_time,
                limit=1000  # Limit to prevent too many requests
            )
            
            if not tx_versions:
                return None
            
            # Process transactions and aggregate fees
            total_fees_token0 = Decimal("0")
            total_fees_token1 = Decimal("0")
            processed_count = 0
            
            for tx_version in tx_versions:
                try:
                    # Fetch fungible asset activities for this transaction
                    activities = await self.fetch_fungible_asset_activities_for_transaction(tx_version)
                    
                    if not activities:
                        continue
                    
                    # Parse activities using adapter
                    parsed = adapter.parse_fees_from_activities(
                        activities,
                        pool_address,
                        token0_address,
                        token1_address
                    )
                    
                    if parsed:
                        total_fees_token0 += parsed.get("fee_token0", Decimal("0"))
                        total_fees_token1 += parsed.get("fee_token1", Decimal("0"))
                        processed_count += 1
                except Exception as e:
                    print(f"Error processing transaction {tx_version}: {e}")
                    continue
            
            if processed_count == 0:
                return None
            
            # Convert fees to USD using price oracle
            fees_usd = await self.price_oracle.convert_fees_to_usd(
                total_fees_token0,
                total_fees_token1,
                token0_address,
                token1_address,
                token0_decimals,
                token1_decimals
            )
            
            # Return None if prices unavailable (don't approximate)
            return {
                "fees_usd": float(fees_usd) if fees_usd else None,
                "fees_token0": float(total_fees_token0),
                "fees_token1": float(total_fees_token1),
                "swap_count": processed_count,
                "updated_at": datetime.utcnow().isoformat(),
                "source": "aptos_indexer",
            }
        except Exception as e:
            print(f"Error getting real fees from Aptos Indexer for {pool_address}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def fetch_pools_for_dex(
        self, 
        chain: str = "aptos", 
        dex_slug: str = None
    ) -> List[Dict[str, Any]]:
        """
        Level 3: Not used for fetching pool list
        Pool list comes from Dexscreener (Level 2)
        This provider only calculates real fees
        """
        return []
    
    async def search_pools(
        self, 
        chain: str = "aptos", 
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Level 3: Not used for searching pools
        Pool search comes from Dexscreener (Level 2)
        """
        return []
    
    
    async def close(self):
        """Close HTTP client and price oracle"""
        await self.client.aclose()
        await self.price_oracle.close()

