"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.pool_index import start_preload_index

from .cache import close_redis
from .routers import aggregator, strategies


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


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    start_preload_index()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_redis()
