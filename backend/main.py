"""
Genora Terminal API - Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
# Import models to register them with Base
from app.models import Dex, DexMetricsDaily, Pool, PoolMetricsDaily


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to Redis cache
    from app.core.cache import cache_service
    await cache_service.connect()
    
    # Start scheduler if enabled
    if settings.SCHEDULER_ENABLED:
        from app.core.scheduler import start_scheduler
        start_scheduler()
    
    yield
    
    # Shutdown
    if settings.SCHEDULER_ENABLED:
        from app.core.scheduler import stop_scheduler
        stop_scheduler()
    
    # Close Redis connection
    await cache_service.close()


app = FastAPI(
    title="Genora Terminal API",
    description="DEX and Pool metrics terminal API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        
        # Check Redis connection
        from app.core.cache import cache_service
        if not cache_service.redis_client:
            await cache_service.connect()
        await cache_service.redis_client.ping()
        
        return {
            "status": "ok",
            "service": "genora-terminal-api",
            "database": "connected",
            "redis": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "genora-terminal-api",
            "error": str(e),
        }


@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    try:
        from app.core.database import AsyncSessionLocal
        from app.models import Dex, Pool, DexMetricsDaily, PoolMetricsDaily
        from sqlalchemy import select, func
        
        async with AsyncSessionLocal() as session:
            # Count DEXes
            dex_count_result = await session.execute(select(func.count(Dex.slug)))
            dex_count = dex_count_result.scalar() or 0
            
            # Count Pools
            pool_count_result = await session.execute(select(func.count(Pool.id)))
            pool_count = pool_count_result.scalar() or 0
            
            # Count metrics records
            dex_metrics_count_result = await session.execute(select(func.count(DexMetricsDaily.id)))
            dex_metrics_count = dex_metrics_count_result.scalar() or 0
            
            pool_metrics_count_result = await session.execute(select(func.count(PoolMetricsDaily.id)))
            pool_metrics_count = pool_metrics_count_result.scalar() or 0
        
        return {
            "status": "ok",
            "version": "1.0.0",
            "counts": {
                "dexes": dex_count,
                "pools": pool_count,
                "dex_metrics": dex_metrics_count,
                "pool_metrics": pool_metrics_count,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "version": "1.0.0",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

