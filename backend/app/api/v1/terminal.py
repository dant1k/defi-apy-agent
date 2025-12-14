"""Terminal API endpoints"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.cache_decorators import cache_dexes, cache_dex_detail, cache_pools
from app.models import Dex, DexMetricsDaily, Pool, PoolMetricsDaily
from app.services.genora_data_service import GenoraDataService

router = APIRouter()


@router.get("/terminal/dexes")
@cache_dexes()
async def get_dexes(
    chain: str = Query(default="aptos", description="Chain name"),
    sort: str = Query(default="tvl_desc", description="Sort order"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of DEXes with optional filtering and sorting"""
    try:
        # Query DEXes from database
        query = select(Dex).where(Dex.chain == chain)
        
        # Apply sorting
        if sort == "tvl_desc":
            # Join with latest metrics for sorting
            query = query.order_by(desc(Dex.updated_at))
        elif sort == "name_asc":
            query = query.order_by(Dex.name)
        else:
            query = query.order_by(desc(Dex.updated_at))
        
        result = await db.execute(query)
        dexes = result.scalars().all()
        
        # Get latest metrics for each DEX
        dex_list = []
        warning = False
        
        for dex in dexes:
            # Get latest metrics
            metrics_query = select(DexMetricsDaily).where(
                DexMetricsDaily.dex_slug == dex.slug
            ).order_by(desc(DexMetricsDaily.date)).limit(1)
            
            metrics_result = await db.execute(metrics_query)
            latest_metrics = metrics_result.scalar_one_or_none()
            
            dex_data = {
                "slug": dex.slug,
                "name": dex.name,
                "chain": dex.chain,
                "url": dex.url,
                "logo_url": dex.logo_url,
                "tvl_usd": float(latest_metrics.tvl_usd) if latest_metrics and latest_metrics.tvl_usd else None,
                "volume_24h_usd": float(latest_metrics.volume_24h_usd) if latest_metrics and latest_metrics.volume_24h_usd else None,
                "fees_24h_usd": float(latest_metrics.fees_24h_usd) if latest_metrics and latest_metrics.fees_24h_usd else None,
                "fees_7d_usd": float(latest_metrics.fees_7d_usd) if latest_metrics and latest_metrics.fees_7d_usd else None,
                "fees_30d_usd": float(latest_metrics.fees_30d_usd) if latest_metrics and latest_metrics.fees_30d_usd else None,
                "cumulative_fees_usd": float(latest_metrics.cumulative_fees_usd) if latest_metrics and latest_metrics.cumulative_fees_usd else None,
                "updated_at": dex.updated_at.isoformat() if dex.updated_at else None,
            }
            
            # Check if data is stale (older than 1 hour)
            if dex.updated_at:
                age = (datetime.utcnow() - dex.updated_at.replace(tzinfo=None)).total_seconds()
                if age > 3600:  # 1 hour
                    warning = True
            
            dex_list.append(dex_data)
        
        # Sort by TVL if requested
        if sort == "tvl_desc":
            dex_list.sort(key=lambda x: x["tvl_usd"] or 0, reverse=True)
        
        return {
            "items": dex_list,
            "total": len(dex_list),
            "chain": chain,
            "warning": warning,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DEXes: {str(e)}")


@router.get("/terminal/dexes/{dex_slug}")
@cache_dex_detail()
async def get_dex_detail(
    dex_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific DEX"""
    try:
        # Get DEX
        result = await db.execute(select(Dex).where(Dex.slug == dex_slug))
        dex = result.scalar_one_or_none()
        
        if not dex:
            raise HTTPException(status_code=404, detail=f"DEX {dex_slug} not found")
        
        # Get latest metrics
        metrics_query = select(DexMetricsDaily).where(
            DexMetricsDaily.dex_slug == dex_slug
        ).order_by(desc(DexMetricsDaily.date)).limit(1)
        
        metrics_result = await db.execute(metrics_query)
        latest_metrics = metrics_result.scalar_one_or_none()
        
        # Get 30-day chart data
        charts_query = select(DexMetricsDaily).where(
            DexMetricsDaily.dex_slug == dex_slug
        ).order_by(DexMetricsDaily.date).limit(30)
        
        charts_result = await db.execute(charts_query)
        charts_data = charts_result.scalars().all()
        
        charts = [
            {
                "timestamp": m.date.isoformat(),
                "tvl_usd": float(m.tvl_usd) if m.tvl_usd else None,
            }
            for m in charts_data
        ]
        
        # Check if data is stale
        warning = False
        if dex.updated_at:
            age = (datetime.utcnow() - dex.updated_at.replace(tzinfo=None)).total_seconds()
            if age > 3600:  # 1 hour
                warning = True
        
        return {
            "slug": dex.slug,
            "name": dex.name,
            "chain": dex.chain,
            "url": dex.url,
            "logo_url": dex.logo_url,
            "tvl_usd": float(latest_metrics.tvl_usd) if latest_metrics and latest_metrics.tvl_usd else None,
            "volume_24h_usd": float(latest_metrics.volume_24h_usd) if latest_metrics and latest_metrics.volume_24h_usd else None,
            "fees_24h_usd": float(latest_metrics.fees_24h_usd) if latest_metrics and latest_metrics.fees_24h_usd else None,
            "fees_7d_usd": float(latest_metrics.fees_7d_usd) if latest_metrics and latest_metrics.fees_7d_usd else None,
            "fees_30d_usd": float(latest_metrics.fees_30d_usd) if latest_metrics and latest_metrics.fees_30d_usd else None,
            "cumulative_fees_usd": float(latest_metrics.cumulative_fees_usd) if latest_metrics and latest_metrics.cumulative_fees_usd else None,
            "charts_30d": charts,
            "updated_at": dex.updated_at.isoformat() if dex.updated_at else None,
            "warning": warning,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DEX detail: {str(e)}")


@router.get("/terminal/dexes/{dex_slug}/pools")
@cache_pools()
async def get_dex_pools(
    dex_slug: str,
    search: Optional[str] = Query(default=None, description="Search query"),
    sort: str = Query(default="tvl_desc", description="Sort order"),
    db: AsyncSession = Depends(get_db),
):
    """Get pools for a specific DEX"""
    try:
        # Verify DEX exists
        dex_result = await db.execute(select(Dex).where(Dex.slug == dex_slug))
        dex = dex_result.scalar_one_or_none()
        
        if not dex:
            raise HTTPException(status_code=404, detail=f"DEX {dex_slug} not found")
        
        # Query pools
        query = select(Pool).where(Pool.dex_slug == dex_slug)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            query = query.where(
                (Pool.token0_symbol.ilike(f"%{search_lower}%")) |
                (Pool.token1_symbol.ilike(f"%{search_lower}%")) |
                (Pool.address.ilike(f"%{search_lower}%"))
            )
        
        result = await db.execute(query)
        pools = result.scalars().all()
        
        # Get latest metrics for each pool
        pool_list = []
        warning = False
        
        for pool in pools:
            # Get latest metrics
            metrics_query = select(PoolMetricsDaily).where(
                PoolMetricsDaily.pool_id == pool.id
            ).order_by(desc(PoolMetricsDaily.date)).limit(1)
            
            metrics_result = await db.execute(metrics_query)
            latest_metrics = metrics_result.scalar_one_or_none()
            
            pool_data = {
                "id": pool.id,
                "dex_slug": pool.dex_slug,
                "chain": pool.chain,
                "token0_address": pool.token0_address,
                "token0_symbol": pool.token0_symbol,
                "token1_address": pool.token1_address,
                "token1_symbol": pool.token1_symbol,
                "address": pool.address,
                "url": pool.url,
                "tvl_usd": float(latest_metrics.tvl_usd) if latest_metrics and latest_metrics.tvl_usd else None,
                "volume_24h_usd": float(latest_metrics.volume_24h_usd) if latest_metrics and latest_metrics.volume_24h_usd else None,
                "fees_24h_usd": float(latest_metrics.fees_24h_usd) if latest_metrics and latest_metrics.fees_24h_usd else None,
                "fees_source": latest_metrics.fees_source if latest_metrics else None,
                "updated_at": pool.updated_at.isoformat() if pool.updated_at else None,
            }
            
            # Check if data is stale
            if pool.updated_at:
                age = (datetime.utcnow() - pool.updated_at.replace(tzinfo=None)).total_seconds()
                if age > 600:  # 10 minutes
                    warning = True
            
            pool_list.append(pool_data)
        
        # Apply sorting
        if sort == "tvl_desc":
            pool_list.sort(key=lambda x: x["tvl_usd"] or 0, reverse=True)
        elif sort == "volume_desc":
            pool_list.sort(key=lambda x: x["volume_24h_usd"] or 0, reverse=True)
        
        return {
            "items": pool_list,
            "total": len(pool_list),
            "dex_slug": dex_slug,
            "warning": warning,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pools: {str(e)}")


@router.get("/terminal/dexes/{dex_slug}/pools/{pool_id}")
async def get_pool_detail(
    dex_slug: str,
    pool_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific pool"""
    try:
        # Get pool
        result = await db.execute(
            select(Pool).where(Pool.id == pool_id, Pool.dex_slug == dex_slug)
        )
        pool = result.scalar_one_or_none()
        
        if not pool:
            raise HTTPException(status_code=404, detail=f"Pool {pool_id} not found")
        
        # Get latest metrics
        metrics_query = select(PoolMetricsDaily).where(
            PoolMetricsDaily.pool_id == pool_id
        ).order_by(desc(PoolMetricsDaily.date)).limit(1)
        
        metrics_result = await db.execute(metrics_query)
        latest_metrics = metrics_result.scalar_one_or_none()
        
        # Get 30-day chart data
        charts_query = select(PoolMetricsDaily).where(
            PoolMetricsDaily.pool_id == pool_id
        ).order_by(PoolMetricsDaily.date).limit(30)
        
        charts_result = await db.execute(charts_query)
        charts_data = charts_result.scalars().all()
        
        charts = [
            {
                "timestamp": m.date.isoformat(),
                "tvl_usd": float(m.tvl_usd) if m.tvl_usd else None,
                "volume_24h_usd": float(m.volume_24h_usd) if m.volume_24h_usd else None,
                "fees_24h_usd": float(m.fees_24h_usd) if m.fees_24h_usd else None,
            }
            for m in charts_data
        ]
        
        # Check if data is stale
        warning = False
        if pool.updated_at:
            age = (datetime.utcnow() - pool.updated_at.replace(tzinfo=None)).total_seconds()
            if age > 600:  # 10 minutes
                warning = True
        
        return {
            "id": pool.id,
            "dex_slug": pool.dex_slug,
            "chain": pool.chain,
            "token0_address": pool.token0_address,
            "token0_symbol": pool.token0_symbol,
            "token1_address": pool.token1_address,
            "token1_symbol": pool.token1_symbol,
            "address": pool.address,
            "url": pool.url,
            "tvl_usd": float(latest_metrics.tvl_usd) if latest_metrics and latest_metrics.tvl_usd else None,
            "volume_24h_usd": float(latest_metrics.volume_24h_usd) if latest_metrics and latest_metrics.volume_24h_usd else None,
            "fees_24h_usd": float(latest_metrics.fees_24h_usd) if latest_metrics and latest_metrics.fees_24h_usd else None,
            "fees_source": latest_metrics.fees_source if latest_metrics else None,
            "charts_30d": charts,
            "updated_at": pool.updated_at.isoformat() if pool.updated_at else None,
            "warning": warning,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pool detail: {str(e)}")

