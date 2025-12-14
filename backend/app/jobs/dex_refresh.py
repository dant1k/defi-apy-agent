"""Job for refreshing DEX data"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models import Dex, DexMetricsDaily
from app.services.genora_data_service import GenoraDataService
from app.core.config import settings


async def refresh_dexes_job():
    """Refresh DEX list and metrics for all chains (default: aptos)"""
    start_time = datetime.utcnow()
    print(f"[JOB] [{start_time.isoformat()}] Starting refresh_dexes job")
    
    service = GenoraDataService()
    try:
        chain = "aptos"  # Default chain
        
        # Fetch DEX list from provider
        dexes = await service.get_dex_list(chain)
        print(f"[JOB] Fetched {len(dexes)} DEXes from provider")
        
        async with AsyncSessionLocal() as session:
            # Upsert DEX records
            for dex_data in dexes:
                slug = dex_data.get("slug")
                if not slug:
                    continue
                
                # Check if DEX exists
                result = await session.execute(
                    select(Dex).where(Dex.slug == slug)
                )
                existing_dex = result.scalar_one_or_none()
                
                if existing_dex:
                    # Update existing
                    existing_dex.name = dex_data.get("name", existing_dex.name)
                    existing_dex.chain = dex_data.get("chain", existing_dex.chain)
                    existing_dex.url = dex_data.get("url", existing_dex.url)
                    existing_dex.logo_url = dex_data.get("logo_url", existing_dex.logo_url)
                    existing_dex.updated_at = datetime.utcnow()
                else:
                    # Create new
                    new_dex = Dex(
                        slug=slug,
                        name=dex_data.get("name", ""),
                        chain=dex_data.get("chain", chain),
                        url=dex_data.get("url"),
                        logo_url=dex_data.get("logo_url"),
                    )
                    session.add(new_dex)
                
                # Fetch and save metrics (Level 1: DefiLlama only)
                metrics = await service.get_dex_metrics(slug, chain=chain)
                
                # For Hyperion: aggregate metrics from pools if DefiLlama doesn't provide volume/fees
                if slug == "hyperion" and metrics:
                    # Aggregate volume and fees from pools
                    from app.models import Pool, PoolMetricsDaily
                    from sqlalchemy import func
                    
                    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Aggregate pool metrics
                    result = await session.execute(
                        select(
                            func.sum(PoolMetricsDaily.volume_24h_usd).label("total_volume"),
                            func.sum(PoolMetricsDaily.fees_24h_usd).label("total_fees")
                        )
                        .join(Pool, Pool.id == PoolMetricsDaily.pool_id)
                        .where(Pool.dex_slug == "hyperion")
                        .where(PoolMetricsDaily.date == today)
                    )
                    agg_result = result.first()
                    
                    if agg_result:
                        # Use aggregated values if DefiLlama doesn't provide them
                        if not metrics.get("volume_24h_usd") and agg_result.total_volume:
                            metrics["volume_24h_usd"] = float(agg_result.total_volume)
                        if not metrics.get("fees_24h_usd") and agg_result.total_fees:
                            metrics["fees_24h_usd"] = float(agg_result.total_fees)
                
                if metrics:
                    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Check if metrics for today exist
                    result = await session.execute(
                        select(DexMetricsDaily).where(
                            DexMetricsDaily.dex_slug == slug,
                            DexMetricsDaily.date == today
                        )
                    )
                    existing_metrics = result.scalar_one_or_none()
                    
                    if existing_metrics:
                        # Update existing
                        existing_metrics.tvl_usd = metrics.get("tvl_usd")
                        existing_metrics.volume_24h_usd = metrics.get("volume_24h_usd")
                        existing_metrics.fees_24h_usd = metrics.get("fees_24h_usd")
                        existing_metrics.fees_7d_usd = metrics.get("fees_7d_usd")
                        existing_metrics.fees_30d_usd = metrics.get("fees_30d_usd")
                        existing_metrics.cumulative_fees_usd = metrics.get("cumulative_fees_usd")
                    else:
                        # Create new
                        new_metrics = DexMetricsDaily(
                            dex_slug=slug,
                            date=today,
                            tvl_usd=metrics.get("tvl_usd"),
                            volume_24h_usd=metrics.get("volume_24h_usd"),
                            fees_24h_usd=metrics.get("fees_24h_usd"),
                            fees_7d_usd=metrics.get("fees_7d_usd"),
                            fees_30d_usd=metrics.get("fees_30d_usd"),
                            cumulative_fees_usd=metrics.get("cumulative_fees_usd"),
                        )
                        session.add(new_metrics)
            
            await session.commit()
            duration = (datetime.utcnow() - start_time).total_seconds()
            print(f"[JOB] [{datetime.utcnow().isoformat()}] Successfully refreshed {len(dexes)} DEXes in {duration:.2f}s")
    
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        print(f"[JOB] [{datetime.utcnow().isoformat()}] ERROR in refresh_dexes after {duration:.2f}s: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await service.close()

