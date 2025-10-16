import os
import json
import requests
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(prefix="/cmc", tags=["CMC"])

CMC_API_KEY = os.getenv("NEXT_PUBLIC_CMC_API_KEY")
BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# Папки для кэша
ICONS_DIR_TOKENS = "api/static/icons/tokens"
ICONS_DIR_CHAINS = "api/static/icons/chains"
CACHE_FILE_TOKENS = "api/static/cache/tokens.json"
CACHE_FILE_CHAINS = "api/static/cache/chains.json"

os.makedirs(ICONS_DIR_TOKENS, exist_ok=True)
os.makedirs(ICONS_DIR_CHAINS, exist_ok=True)
os.makedirs(os.path.dirname(CACHE_FILE_TOKENS), exist_ok=True)


def fetch_from_cmc(endpoint, params=None):
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def save_icon(icon_url: str, path: str):
    try:
        img = requests.get(icon_url, timeout=5)
        if img.status_code == 200:
            with open(path, "wb") as f:
                f.write(img.content)
    except Exception:
        pass


@router.get("/tokens")
def get_tokens(limit: int = 100):
    if os.path.exists(CACHE_FILE_TOKENS):
        with open(CACHE_FILE_TOKENS, "r") as f:
            data = json.load(f)
            return {"count": len(data), "tokens": data[:limit]}

    res = fetch_from_cmc("cryptocurrency/listings/latest", {"limit": limit})
    tokens = []
    for d in res["data"]:
        icon_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{d['id']}.png"
        path = f"{ICONS_DIR_TOKENS}/{d['symbol']}.png"
        save_icon(icon_url, path)
        tokens.append({
            "name": d["name"],
            "symbol": d["symbol"],
            "icon": f"/icons/tokens/{d['symbol']}.png"
        })

    with open(CACHE_FILE_TOKENS, "w") as f:
        json.dump(tokens, f)

    return {"count": len(tokens), "tokens": tokens}


@router.get("/chains")
def get_chains(limit: int = 200):
    if os.path.exists(CACHE_FILE_CHAINS):
        with open(CACHE_FILE_CHAINS, "r") as f:
            data = json.load(f)
            return {"count": len(data), "chains": data[:limit]}

    # Для простоты берём топ токенов как chains
    res = fetch_from_cmc("cryptocurrency/listings/latest", {"limit": limit})
    chains = []
    for d in res["data"]:
        icon_url = f"https://s2.coinmarketcap.com/static/img/coins/64x64/{d['id']}.png"
        path = f"{ICONS_DIR_CHAINS}/{d['name']}.png"
        save_icon(icon_url, path)
        chains.append({
            "name": d["name"],
            "symbol": d["symbol"],
            "icon": f"/icons/chains/{d['name']}.png"
        })

    with open(CACHE_FILE_CHAINS, "w") as f:
        json.dump(chains, f)

    return {"count": len(chains), "chains": chains}