from fastapi import APIRouter
import httpx
import os
import time

router = APIRouter(prefix="/cmc", tags=["CoinMarketCap"])
CMC_API_KEY = os.getenv("CMC_API_KEY")

cache = {"tokens": None, "chains": None, "timestamp": 0}

@router.get("/tokens")
async def get_top_tokens(limit: int = 100):
    if not CMC_API_KEY:
        return {"error": "CMC_API_KEY not set"}

    if cache["tokens"] and time.time() - cache["timestamp"] < 3600:
        return cache["tokens"]

    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit={limit}"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()

    tokens = [
        {
            "name": t["name"],
            "symbol": t["symbol"],
            "icon": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{t['id']}.png",
        }
        for t in data.get("data", [])
    ]

    result = {"count": len(tokens), "tokens": tokens}
    cache["tokens"] = result
    cache["timestamp"] = time.time()
    return result


@router.get("/chains")
async def get_chains(limit: int = 200):
    """Возвращает layer-1 сети с иконками"""
    if not CMC_API_KEY:
        return {"error": "CMC_API_KEY not set"}

    if cache["chains"] and time.time() - cache["timestamp"] < 3600:
        return cache["chains"]

    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit={limit}"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()

    layer1_tags = ["layer-1", "binance-ecosystem", "solana-ecosystem", "ethereum-ecosystem"]
    chains = [
        {
            "name": t["name"],
            "symbol": t["symbol"],
            "icon": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{t['id']}.png",
        }
        for t in data.get("data", [])
        if any(tag in t.get("tags", []) for tag in layer1_tags)
    ]

    result = {"count": len(chains), "chains": chains}
    cache["chains"] = result
    cache["timestamp"] = time.time()
    return result