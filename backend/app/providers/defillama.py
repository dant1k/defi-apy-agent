"""DefiLlama provider implementation"""
import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from app.providers.base import DexMetricsProvider
from app.core.config import settings


class DefiLlamaProvider(DexMetricsProvider):
    """DefiLlama API provider for DEX metrics"""
    
    def __init__(self):
        self.base_url = settings.DEFILLAMA_API_URL
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def fetch_dex_list_by_chain(self, chain: str = "aptos") -> List[Dict[str, Any]]:
        """Fetch DEX list from DefiLlama by chain"""
        try:
            # Use /v2/protocols endpoint and filter by chain
            url = f"{self.base_url}/v2/protocols"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            dexes = []
            if isinstance(data, list):
                print(f"[DefiLlama] Received {len(data)} total protocols")
                aptos_count = 0
                for protocol in data:
                    # Check chainTvls for the requested chain (chains are keys in chainTvls dict)
                    chain_tvls = protocol.get("chainTvls", {})
                    chain_names = [c.lower() for c in chain_tvls.keys()] if isinstance(chain_tvls, dict) else []
                    
                    # Check if protocol is on the requested chain
                    if chain.lower() in chain_names:
                        aptos_count += 1
                        # Filter for DEX protocols (category or name contains DEX)
                        name = protocol.get("name", "").lower()
                        category = protocol.get("category", "").lower()
                        # Include DEX/exchange protocols
                        if "dex" in name or "dex" in category or "exchange" in category or "amm" in name:
                            # Get slug - prefer slug field, fallback to name-based slug
                            slug = protocol.get("slug")
                            if not slug:
                                # Create slug from name
                                slug = protocol.get("name", "").lower().replace(" ", "-").replace("'", "").replace(".", "")
                            # Store both slug and id for reference
                            dex_id = protocol.get("id")
                            dexes.append({
                                "slug": slug,
                                "name": protocol.get("name", ""),
                                "chain": chain,
                                "url": protocol.get("url", ""),
                                "logo_url": protocol.get("logo", ""),
                                "defillama_id": dex_id,  # Store ID for reference
                            })
                print(f"[DefiLlama] Found {aptos_count} protocols on {chain}, {len(dexes)} DEXes")
            else:
                print(f"[DefiLlama] Unexpected data type: {type(data)}")
            
            return dexes
        except Exception as e:
            print(f"Error fetching DEX list from DefiLlama: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def fetch_dex_metrics(
        self, 
        dex_slug: str, 
        timeframe: str = "1d"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch DEX metrics from DefiLlama
        Level 1: Uses DefiLlama for TVL and Fees (24h/7d/30d/cumulative)
        """
        try:
            # Get TVL from protocol endpoint
            url = f"{self.base_url}/protocol/{dex_slug}"
            response = await self.client.get(url)
            
            if response.status_code == 404:
                url = f"{self.base_url}/v2/protocol/{dex_slug}"
                response = await self.client.get(url)
            
            response.raise_for_status()
            protocol_data = response.json()
            
            if not protocol_data or not isinstance(protocol_data, dict):
                return None
            
            # Extract TVL
            tvl_usd = Decimal("0")
            if "tvl" in protocol_data and isinstance(protocol_data["tvl"], (int, float)):
                tvl_usd = Decimal(str(protocol_data["tvl"]))
            elif "tvl" in protocol_data and isinstance(protocol_data["tvl"], list) and len(protocol_data["tvl"]) > 0:
                tvl_usd = Decimal(str(protocol_data["tvl"][-1].get("totalLiquidityUSD", 0)))
            
            # Get Fees from /fees endpoint (Level 1: DefiLlama fees/revenue)
            fees_24h_usd = None
            fees_7d_usd = None
            fees_30d_usd = None
            cumulative_fees_usd = None
            
            try:
                fees_url = f"{self.base_url}/fees/{dex_slug}"
                fees_response = await self.client.get(fees_url, timeout=10.0)
                
                if fees_response.status_code == 200:
                    fees_data = fees_response.json()
                    if isinstance(fees_data, dict):
                        # DefiLlama fees endpoint structure
                        fees_24h_usd = fees_data.get("fees24h")
                        fees_7d_usd = fees_data.get("fees7d")
                        fees_30d_usd = fees_data.get("fees30d")
                        cumulative_fees_usd = fees_data.get("totalFees")
                        
                        # Convert to Decimal if they exist
                        if fees_24h_usd is not None:
                            fees_24h_usd = float(Decimal(str(fees_24h_usd)))
                        if fees_7d_usd is not None:
                            fees_7d_usd = float(Decimal(str(fees_7d_usd)))
                        if fees_30d_usd is not None:
                            fees_30d_usd = float(Decimal(str(fees_30d_usd)))
                        if cumulative_fees_usd is not None:
                            cumulative_fees_usd = float(Decimal(str(cumulative_fees_usd)))
            except Exception as e:
                # Fees endpoint might not be available for all protocols
                print(f"Could not fetch fees from DefiLlama for {dex_slug}: {e}")
                pass
            
            return {
                "tvl_usd": float(tvl_usd) if tvl_usd > 0 else None,
                "volume_24h_usd": None,  # Not from DefiLlama for DEX level
                "fees_24h_usd": fees_24h_usd,
                "fees_7d_usd": fees_7d_usd,
                "fees_30d_usd": fees_30d_usd,
                "cumulative_fees_usd": cumulative_fees_usd,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            print(f"Error fetching DEX metrics from DefiLlama for {dex_slug}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching DEX metrics from DefiLlama for {dex_slug}: {e}")
            return None
    
    async def fetch_dex_charts_30d(self, dex_slug: str) -> List[Dict[str, Any]]:
        """Fetch 30-day chart data for a DEX"""
        try:
            url = f"{self.base_url}/protocol/{dex_slug}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data or not isinstance(data, dict):
                return []
            
            # Extract historical data
            charts = []
            historical_tvl = data.get("tvl", [])
            
            # Get last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            for point in historical_tvl:
                if isinstance(point, dict):
                    timestamp = point.get("date", 0)
                    if timestamp:
                        point_date = datetime.fromtimestamp(timestamp)
                        if start_date <= point_date <= end_date:
                            charts.append({
                                "timestamp": point_date.isoformat(),
                                "tvl_usd": float(Decimal(str(point.get("totalLiquidityUSD", 0)))),
                            })
            
            return sorted(charts, key=lambda x: x["timestamp"])
        except Exception as e:
            print(f"Error fetching DEX charts from DefiLlama for {dex_slug}: {e}")
            return []
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

