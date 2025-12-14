"""API v1 router"""
from fastapi import APIRouter
from app.api.v1 import chains, terminal, admin

api_router = APIRouter()

# Include routers
api_router.include_router(chains.router, tags=["chains"])
api_router.include_router(terminal.router, tags=["terminal"])
api_router.include_router(admin.router, tags=["admin"])

