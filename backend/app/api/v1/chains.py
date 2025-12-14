"""Chains endpoint"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/chains", response_model=List[str])
async def get_chains():
    """Get list of supported chains"""
    # For now, return default chain
    # Can be extended to fetch from database or config
    return ["aptos"]


