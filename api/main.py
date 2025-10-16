"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.pool_index import start_preload_index

from .cache import close_redis
from .routers import aggregator, strategies
from .routers import cmc_cache


app = FastAPI(title="DeFi APY Agent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(aggregator.router)
app.include_router(strategies.router)
app.include_router(cmc_cache.router)

# Serve cached icons from API under /icons/... (tokens, chains)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@app.get("/icons/{category}/{filename}")
async def serve_icon(category: str, filename: str):
    """Serve icons from backup with proper CORS headers"""
    full_path = f"api/static/icons/{category}/{filename}"
    if os.path.exists(full_path):
        return FileResponse(
            full_path,
            media_type="image/png",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
            }
        )
    return {"error": "Icon not found"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    start_preload_index()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_redis()
