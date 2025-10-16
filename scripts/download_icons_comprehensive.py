#!/usr/bin/env python3
"""
Комплексный скрипт для загрузки иконок из CoinGecko, CoinMarketCap и DeFiLlama.
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
FRONTEND_ICONS_DIR = Path("frontend/public/icons")
API_ICONS_DIR = Path("api/static/icons")

# API ключи
COINMARKETCAP_API_KEY = "4dc743a6ee7f4294a2d34f2969e37014"

# Создаем директории
for category in ["chains", "protocols", "tokens"]:
    (FRONTEND_ICONS_DIR / category).mkdir(parents=True, exist_ok=True)
    (API_ICONS_DIR / category).mkdir(parents=True, exist_ok=True)

# Недостающие элементы из проверки
MISSING_ITEMS = {
    "chains": [
        "Aptos", "Arbitrum", "BSC", "Core", "Filecoin", "Flare", "Flow", "Fraxtal",
        "Fuel-ignition", "Hemi", "Hyperliquid", "Mainnet", "MultiversX", "Neo",
        "Osmosis", "Starknet", "Stellar", "Ton"
    ],
    "protocols": [
        "40-acres", "aerodrome-slipstream", "aerodrome-v1", "autofinance", "avantis",
        "balancer-v2", "balancer-v3", "beefy", "beets-dex", "beets-dex-v3",
        "blend-pools-v2", "bmx-classic-perps", "camelot-v2", "camelot-v3", "cetus-amm",
        "colend-protocol", "comb-financial", "concentrator", "convex-finance", "curve-dex",
        "dedust", "deltaprime", "etherex-cl", "euler-v2", "extra-finance-leverage-farming",
        "flamingo-finance", "flex-perpetuals", "flowx-v3", "francium", "frax", "fraxlend",
        "full-sail", "fx-protocol", "gains-network", "gearbox", "gmx-v2-perps",
        "harmonix-finance", "hydration-dex", "hyperion", "indigo", "ipor-fusion",
        "joe-v2.1", "kai-finance", "kamino-liquidity", "kinetic", "lagoon", "liqwid",
        "lista-lending", "mainstreet", "midas-rwa", "minswap", "more-markets",
        "navi-lending", "nostra-pools", "notional-v3", "orca-dex", "origami-finance",
        "osmosis-dex", "pancakeswap-amm", "pancakeswap-amm-v3", "peapods-finance",
        "raydium-amm", "sceptre-liquid", "sft-protocol", "shadow-exchange-clmm",
        "sparkdex-v3.1", "spectra-v2", "stable-jack-v1", "stake-dao", "storm-trade",
        "stream-finance", "superfund", "superlend", "sushiswap", "sushiswap-v3",
        "takara-lend", "tapp-exchange", "thalaswap-v2", "tonco", "toros", "troves",
        "uniswap-v2", "uniswap-v3", "upshift", "usual", "vvs-standard",
        "wildcat-protocol", "wink", "xexchange", "yearn-finance", "yieldnest"
    ],
    "tokens": [
        "AERO", "AEVO", "ALUSD", "API3", "ASTR", "AURA", "BALANCER", "BIFI", "BMX",
        "BONK", "CRV", "CRVUSD", "DEGEN", "ENA", "EPENDLE", "EURC", "EUROC", "EUSD",
        "EZETH", "FRAX", "FRAXBP", "FRXUSD", "FTM", "FUEL", "FXS", "GHO", "GLMR",
        "JITOSOL", "JLP", "JTO", "JUP", "LDO", "LINEA", "MORPHO", "MSOL", "PENDLE",
        "PYUSD", "RAY", "RENDER", "RLUSD", "RSETH", "SEI", "SNX", "SPX", "STRK",
        "SUSDE", "SYRUP", "USDC.E", "USDF", "USDT0", "USD1", "USDAI", "VIRTUAL",
        "WBNB", "XAUT", "YFI"
    ]
}

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL."""
    try:
        if not url or not url.startswith('http'):
            return False

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {path.name}")
            return True
    except Exception as e:
        print(f"✗ Failed {path.name}: {e}")
    return False

def get_coin_icon_from_gecko(gecko_id: str) -> str:
    """Получить URL иконки из CoinGecko по gecko_id."""
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except:
        pass
    return ""

def search_coin_icon_by_name(name: str) -> str:
    """Поиск иконки по имени в CoinGecko."""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": name
        })
        if response.status_code == 200:
            data = response.json()
            coins = data.get("coins", [])
            if coins:
                return get_coin_icon_from_gecko(coins[0]["id"])
    except:
        pass
    return ""

def get_coin_icon_from_cmc(symbol: str) -> str:
    """Получить URL иконки из CoinMarketCap."""
    try:
        headers = {
            'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
            'Accept': 'application/json'
        }
        
        # Сначала получаем ID токена
        response = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
            headers=headers,
            params={'symbol': symbol}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                coin_id = data['data'][0]['id']
                
                # Получаем метаданные с логотипом
                meta_response = requests.get(
                    f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info",
                    headers=headers,
                    params={'id': coin_id}
                )
                
                if meta_response.status_code == 200:
                    meta_data = meta_response.json()
                    if meta_data.get('data', {}).get(str(coin_id)):
                        logo_url = meta_data['data'][str(coin_id)].get('logo')
                        if logo_url:
                            return logo_url
    except Exception as e:
        print(f"CoinMarketCap error for {symbol}: {e}")
    return ""

def get_defillama_icon(name: str, category: str) -> str:
    """Получить URL иконки из DeFiLlama."""
    try:
        if category == "chains":
            return f"https://icons.llama.fi/{name.lower()}.png"
        elif category == "protocols":
            return f"https://icons.llama.fi/{name.lower()}.png"
        elif category == "tokens":
            return f"https://icons.llama.fi/tokens/{name.lower()}.png"
    except:
        pass
    return ""

def normalize_name(name: str, category: str) -> str:
    """Нормализует имя для поиска иконки."""
    if category == "chains":
        return name.upper().replace(" ", "").replace("-", "")
    elif category == "protocols":
        return name.upper().replace(" ", "").replace("-", "").replace("_", "")
    else:  # tokens
        return name.upper()

def download_icons_for_category(category: str, items: list):
    """Загружает иконки для категории."""
    print(f"\n🔍 Загружаем иконки {category}...")
    
    downloaded = 0
    failed = 0
    
    for item in items:
        normalized = normalize_name(item, category)
        icon_file = f"{normalized}.png"
        
        frontend_path = FRONTEND_ICONS_DIR / category / icon_file
        api_path = API_ICONS_DIR / category / icon_file
        
        # Пропускаем если уже есть
        if frontend_path.exists() and api_path.exists():
            print(f"✓ {item} - уже есть")
            continue
        
        print(f"🔍 Ищем иконку для {item}...")
        
        icon_url = ""
        
        # Пробуем разные источники
        if category == "tokens":
            # Для токенов пробуем CoinMarketCap, затем CoinGecko
            icon_url = get_coin_icon_from_cmc(item)
            if not icon_url:
                icon_url = search_coin_icon_by_name(item)
        else:
            # Для сетей и протоколов пробуем DeFiLlama, затем CoinGecko
            icon_url = get_defillama_icon(item, category)
            if not icon_url:
                icon_url = search_coin_icon_by_name(item)
        
        if icon_url:
            # Скачиваем в frontend
            if not frontend_path.exists():
                if download_image(icon_url, frontend_path):
                    downloaded += 1
                else:
                    failed += 1
                    continue
            
            # Копируем в API
            if not api_path.exists():
                try:
                    with open(frontend_path, 'rb') as src, open(api_path, 'wb') as dst:
                        dst.write(src.read())
                    print(f"✓ Copied to API: {icon_file}")
                except Exception as e:
                    print(f"✗ Failed to copy to API: {e}")
                    failed += 1
        else:
            print(f"✗ Не удалось найти иконку для {item}")
            failed += 1
        
        # Небольшая задержка между запросами
        time.sleep(0.5)
    
    print(f"📊 {category}: ✓ {downloaded}, ✗ {failed}")
    return downloaded, failed

def main():
    """Основная функция."""
    print("🚀 Комплексная загрузка иконок из всех источников...")
    print(f"📁 Frontend: {FRONTEND_ICONS_DIR}")
    print(f"📁 API: {API_ICONS_DIR}")
    
    total_downloaded = 0
    total_failed = 0
    
    for category, items in MISSING_ITEMS.items():
        downloaded, failed = download_icons_for_category(category, items)
        total_downloaded += downloaded
        total_failed += failed
    
    print(f"\n🎉 ИТОГО:")
    print(f"✓ Загружено: {total_downloaded}")
    print(f"✗ Не удалось: {total_failed}")

if __name__ == "__main__":
    main()

