"""Job for refreshing Pool data for top DEXes"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models import Dex, Pool, PoolMetricsDaily
from app.services.genora_data_service import GenoraDataService
from app.core.config import settings


async def refresh_pools_top_dexes_job():
    """Refresh pools for top N DEXes"""
    start_time = datetime.utcnow()
    print(f"[JOB] [{start_time.isoformat()}] Starting refresh_pools_top_dexes job")
    
    service = GenoraDataService()
    try:
        chain = "aptos"  # Default chain
        top_n = settings.TOP_DEXES_COUNT
        
        async with AsyncSessionLocal() as session:
            # Get top N DEXes by TVL (or just get first N)
            result = await session.execute(
                select(Dex)
                .where(Dex.chain == chain)
                .order_by(Dex.updated_at.desc())
                .limit(top_n)
            )
            top_dexes = result.scalars().all()
            
            # Always include Hyperion if it exists (important for Hyperion API integration)
            hyperion_result = await session.execute(
                select(Dex).where(Dex.slug == "hyperion", Dex.chain == chain)
            )
            hyperion_dex = hyperion_result.scalar_one_or_none()
            if hyperion_dex and hyperion_dex not in top_dexes:
                top_dexes.append(hyperion_dex)
                print(f"[JOB] Added Hyperion to refresh list (not in top {top_n})")
            
            print(f"[JOB] Found {len(top_dexes)} top DEXes to refresh pools for")
            
            for dex in top_dexes:
                try:
                    # Fetch pools for this DEX
                    pools = await service.get_pools_for_dex(chain, dex.slug)
                    print(f"[JOB] Fetched {len(pools)} pools for DEX {dex.slug}")
                    
                    for pool_data in pools:
                        pool_id = pool_data.get("id")
                        if not pool_id:
                            continue
                        
                        # Check if pool exists
                        result = await session.execute(
                            select(Pool).where(Pool.id == pool_id)
                        )
                        existing_pool = result.scalar_one_or_none()
                        
                        if existing_pool:
                            # Update existing
                            existing_pool.dex_slug = pool_data.get("dex_slug", existing_pool.dex_slug)
                            existing_pool.chain = pool_data.get("chain", existing_pool.chain)
                            existing_pool.token0_address = pool_data.get("token0_address")
                            # Update token symbols if they were missing or if new data is available
                            if pool_data.get("token0_symbol"):
                                existing_pool.token0_symbol = pool_data.get("token0_symbol")
                            existing_pool.token1_address = pool_data.get("token1_address")
                            if pool_data.get("token1_symbol"):
                                existing_pool.token1_symbol = pool_data.get("token1_symbol")
                            existing_pool.address = pool_data.get("address")
                            existing_pool.url = pool_data.get("url")
                            existing_pool.updated_at = datetime.utcnow()
                        else:
                            # Create new
                            new_pool = Pool(
                                id=pool_id,
                                dex_slug=pool_data.get("dex_slug", dex.slug),
                                chain=pool_data.get("chain", chain),
                                token0_address=pool_data.get("token0_address"),
                                token0_symbol=pool_data.get("token0_symbol"),
                                token1_address=pool_data.get("token1_address"),
                                token1_symbol=pool_data.get("token1_symbol"),
                                address=pool_data.get("address"),
                                url=pool_data.get("url"),
                            )
                            session.add(new_pool)
                        
                        # Get metrics based on DEX
                        fees_24h_usd = pool_data.get("fees_24h_usd")
                        fees_source = None
                        
                        # For Hyperion: use Hyperion API data (already fetched)
                        if dex.slug == "hyperion":
                            fees_24h_usd = pool_data.get("fees_24h_usd")
                            fees_source = "hyperion_api" if fees_24h_usd else None
                        else:
                            # Level 2: Get metrics from Dexscreener
                            fees_24h_usd = pool_data.get("fees_24h_usd")
                            fees_source = "dexscreener" if fees_24h_usd else None
                            
                            # Level 3: Try to get real fees from Aptos Indexer
                            # Only for top pools (with address and token addresses)
                            pool_address = pool_data.get("address") or pool_id
                            token0_address = pool_data.get("token0_address")
                            token1_address = pool_data.get("token1_address")
                            
                            if pool_address and token0_address and token1_address:
                                try:
                                    real_fees = await service.get_pool_real_fees(
                                        chain=chain,
                                        dex_slug=dex.slug,
                                        pool_address=pool_address,
                                        token0_address=token0_address,
                                        token1_address=token1_address,
                                        token0_decimals=8,  # TODO: Get from token metadata
                                        token1_decimals=8,
                                        timeframe="24h"
                                    )
                                    
                                    if real_fees and real_fees.get("fees_usd") is not None:
                                        # Level 3 succeeded - use real fees
                                        fees_24h_usd = real_fees.get("fees_usd")
                                        fees_source = "aptos_indexer"
                                        print(f"[JOB] Level 3 fees for pool {pool_id}: ${fees_24h_usd:,.2f}")
                                except Exception as e:
                                    # Level 3 failed - keep Level 2 or null
                                    print(f"[JOB] Level 3 failed for pool {pool_id}: {e}")
                                    pass
                        
                        # Save metrics
                        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                        
                        result = await session.execute(
                            select(PoolMetricsDaily).where(
                                PoolMetricsDaily.pool_id == pool_id,
                                PoolMetricsDaily.date == today
                            )
                        )
                        existing_metrics = result.scalar_one_or_none()
                        
                        if existing_metrics:
                            # Update existing
                            existing_metrics.tvl_usd = pool_data.get("tvl_usd")
                            existing_metrics.volume_24h_usd = pool_data.get("volume_24h_usd")
                            existing_metrics.fees_24h_usd = fees_24h_usd
                            existing_metrics.fees_source = fees_source
                        else:
                            # Create new
                            new_metrics = PoolMetricsDaily(
                                pool_id=pool_id,
                                date=today,
                                tvl_usd=pool_data.get("tvl_usd"),
                                volume_24h_usd=pool_data.get("volume_24h_usd"),
                                fees_24h_usd=fees_24h_usd,
                                fees_source=fees_source,
                            )
                            session.add(new_metrics)
                    
                    await session.commit()
                    print(f"[JOB] [{datetime.utcnow().isoformat()}] Successfully refreshed {len(pools)} pools for DEX {dex.slug}")
                
                except Exception as e:
                    print(f"[JOB] [{datetime.utcnow().isoformat()}] ERROR refreshing pools for DEX {dex.slug}: {e}")
                    await session.rollback()
                    continue
        
        duration = (datetime.utcnow() - start_time).total_seconds()
        print(f"[JOB] [{datetime.utcnow().isoformat()}] Completed refresh_pools_top_dexes in {duration:.2f}s")
    
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        print(f"[JOB] [{datetime.utcnow().isoformat()}] ERROR in refresh_pools_top_dexes after {duration:.2f}s: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await service.close()

