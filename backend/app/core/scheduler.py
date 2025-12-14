"""APScheduler configuration"""
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.jobs.dex_refresh import refresh_dexes_job
from app.jobs.pool_refresh import refresh_pools_top_dexes_job

scheduler: Optional[AsyncIOScheduler] = None


def start_scheduler():
    """Start the scheduler and add jobs"""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        
        # Add refresh_dexes job (every 15 minutes)
        scheduler.add_job(
            refresh_dexes_job,
            trigger=IntervalTrigger(minutes=settings.REFRESH_DEXES_INTERVAL_MINUTES),
            id="refresh_dexes",
            name="Refresh DEX list and metrics",
            replace_existing=True,
        )
        
        # Add refresh_pools_top_dexes job (every 10 minutes)
        scheduler.add_job(
            refresh_pools_top_dexes_job,
            trigger=IntervalTrigger(minutes=settings.REFRESH_POOLS_INTERVAL_MINUTES),
            id="refresh_pools_top_dexes",
            name="Refresh pools for top DEXes",
            replace_existing=True,
        )
        
        scheduler.start()
        print("✅ Scheduler started")
        print(f"   - refresh_dexes: every {settings.REFRESH_DEXES_INTERVAL_MINUTES} minutes")
        print(f"   - refresh_pools_top_dexes: every {settings.REFRESH_POOLS_INTERVAL_MINUTES} minutes")


def stop_scheduler():
    """Stop the scheduler"""
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        print("✅ Scheduler stopped")

