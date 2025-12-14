"""Admin endpoints for manual job triggers"""
from fastapi import APIRouter, HTTPException
from app.jobs.dex_refresh import refresh_dexes_job
from app.jobs.pool_refresh import refresh_pools_top_dexes_job

router = APIRouter()


@router.post("/admin/refresh-dexes")
async def trigger_refresh_dexes():
    """Manually trigger refresh_dexes job"""
    try:
        await refresh_dexes_job()
        return {"status": "ok", "message": "refresh_dexes job completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/admin/refresh-pools")
async def trigger_refresh_pools():
    """Manually trigger refresh_pools_top_dexes job"""
    try:
        await refresh_pools_top_dexes_job()
        return {"status": "ok", "message": "refresh_pools_top_dexes job completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

