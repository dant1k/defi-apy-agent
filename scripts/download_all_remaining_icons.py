#!/usr/bin/env python3
"""
Загружает ВСЕ оставшиеся иконки и сохраняет их на бекенде.
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

# Расширенный список всех недостающих элементов
ALL_MISSING_ITEMS = {
    "chains": [
        "BSC", "Core", "Flare", "Flow", "Fuel-ignition", "Mainnet", "MultiversX", 
        "Neo", "Osmosis", "Starknet"
    ],
    "protocols": [
        "40-acres", "aerodrome-slipstream", "aerodrome-v1", "autofinance",
        "balancer-v3", "beets-dex", "beets-dex-v3", "blend-pools-v2", 
        "bmx-classic-perps", "camelot-v3", "colend-protocol", "concentrator",
        "convex-finance", "curve-dex", "deltaprime", "etherex-cl", "euler-v2",
        "extra-finance-leverage-farming", "flamingo-finance", "flex-perpetuals",
        "francium", "frax", "fraxlend", "full-sail", "fx-protocol", "gearbox",
        "harmonix-finance", "hydration-dex", "hyperion", "ipor-fusion", "joe-v2.1",
        "kamino-liquidity", "kinetic", "lagoon", "liqwid", "lista-lending",
        "mainstreet", "midas-rwa", "minswap", "more-markets", "navi-lending",
        "nostra-pools", "notional-v3", "orca-dex", "origami-finance", "osmosis-dex",
        "pancakeswap-amm", "pancakeswap-amm-v3", "peapods-finance", "raydium-amm",
        "sceptre-liquid", "sft-protocol", "shadow-exchange-clmm", "sparkdex-v3.1",
        "spectra-v2", "stable-jack-v1", "stake-dao", "storm-trade", "stream-finance",
        "superfund", "superlend", "sushiswap-v3", "takara-lend", "tapp-exchange",
        "thalaswap-v2", "tonco", "toros", "troves", "uniswap-v2", "uniswap-v3",
        "upshift", "usual", "vvs-standard", "wildcat-protocol", "wink", "xexchange",
        "yearn-finance", "yieldnest"
    ],
    "tokens": [
        "20WETH", "40AVAX", "40BASE", "40OP", "80RZR", "9SUSDC", "ABTC", "ADO",
        "AHORRWARLUSD", "AIDAUSDC", "AIDAUSDT", "AIDOGE", "AITV", "AIXBT", "ALCH",
        "ANYONE", "APEX", "ARC", "ASDCRV", "ASTER", "ATONE", "AU79", "AUDIO",
        "AUKI", "AVA", "AVNT", "B3", "BERT", "BFBTC", "BLOCK", "BNEO", "BOOE",
        "BPT", "BRACKY", "BRETT", "BTC.B", "BTCB", "CARDS", "CBADA", "CBBTC",
        "CBXRP", "CETUS", "CHEX", "CHILLGUY", "CLANKER", "CUSD", "CUSDX", "CVXCRV",
        "DEEP", "DEFI.SSI", "DOLA", "DOOD", "DRB", "DSYNC", "DYFI", "EDGE", "EMP",
        "EPENDLE", "ESFDX", "EUSD", "EZETH", "FARTCOIN", "FBEETS", "FDX", "FET",
        "FLDT", "FLM", "FRAX", "FRAXBP", "FRXUSD", "FTM", "FUEL", "FXRP", "FXS",
        "FXSAVE", "FXUSD", "GAUGE", "GEAR", "GHO", "GLMR", "GOAT", "GRIFFAIN",
        "HAEDAL", "HALALUSDC", "HALALUSDT", "HBUSDT", "HEMI", "HONEY", "HWHLP",
        "IBGT", "IBTC", "IDAI", "IETH", "IKA", "INST", "IUSD", "IUSDC", "IUSDT",
        "JELLYJELLY", "JITOSOL", "JLP", "JTO", "JUP", "KAPT", "KEYCAT", "KODIEWBERA",
        "KODIHOHM", "KODISWBERA", "KODIWBERA", "KODIWBTC", "KODIWETH", "KORI",
        "KTA", "LAUNCHCOIN", "LAYER", "LBGT", "LDO", "LILENGHYUSDC", "LINEA",
        "LLUSDC", "LOCKWINK", "LQTY", "LVEURC", "LVUSDC", "LVUSDCE", "LVUSDT",
        "LVWETH", "MAG7.SSI", "MAMO", "MANYU", "MBOX", "MCADE", "MEDGE", "MEW",
        "MIM", "MMEV", "MOG", "MORI", "MORPHO", "MPENDLE", "MPT", "MSOL", "MSUSD",
        "MSYRUPUSDP", "MUSD", "NOICE", "NOS", "NS", "OASKODIHOHM", "OCEAN", "OHM",
        "OMFG", "ORDER", "ORE", "ORIBGT", "OSBGT", "OVPP", "PAXG", "PEAS", "PENDLE",
        "PIN", "PUPPIES", "PYUSD", "RAD", "RAIL", "RAY", "RDNT", "READY", "RECALL",
        "REI", "RENDER", "RETIRE", "REUSD", "RFG", "RLP", "RLUSD", "RSETH", "RSUP",
        "RUSD", "SAIL", "SATUSD+", "SBOLD", "SBUSDT", "SDBAL", "SDCRV", "SDPENDLE",
        "SEI", "SEND", "SERV", "SFG", "SFLR", "SFT", "SHETOKEN", "SIRE", "SKAITO",
        "SKI", "SKY", "SMSUSD", "SNX", "SPX", "SQD", "STCORE", "STK", "STRIKE",
        "STRK", "STS", "SUIUSDT", "SUPER", "SUPERUSDC", "SURGEEK3SAVUSD", "SUSD",
        "SUSDAI", "SUSDE", "SW", "SWARMS", "SWTCH", "SYND", "SYRUP", "TEL", "THAPT",
        "TITANX", "TON", "TORN", "TRAC", "TRUAPT", "TRWA", "TSLAX", "UPSSYLVA",
        "USD(MIDASMEDGE)", "USD(MIDASMMEV)", "USD+", "USD1", "USDAI", "USDBC",
        "USDC.E", "USDF", "USDP", "USDPY", "USDT0", "USD₮", "USD₮0", "USELESS",
        "USR", "USUALX", "VAULT", "VERTAI", "VFY", "VINE", "VIRTUAL", "VVV",
        "WAETHLIDOGHO", "WAETHUSDC", "WAETHUSDT", "WAL", "WAVAX", "WBERA", "WBLT",
        "WBNB", "WBTC.B", "WCRO", "WEGLD", "WELL", "WETH.E", "WFLR", "WHETH",
        "WMATIC", "WNXM", "WS", "WSOL", "WSTUSR", "WTAO", "WXPL", "WXTZ", "XAUT",
        "XBTC", "XSILO", "XUSD", "YCRV", "YFI", "YNBNBX", "YSYBOLD", "YU", "YUSD",
        "YVBAL", "ZEN", "ZEREBRO", "ZORA"
    ]
}

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL."""
    try:
        if not url or not url.startswith('http'):
            return False

        response = requests.get(url, timeout=15)
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
        
        # Пробуем разные источники в зависимости от категории
        if category == "tokens":
            # Для токенов пробуем CoinMarketCap, затем CoinGecko, затем DeFiLlama
            icon_url = get_coin_icon_from_cmc(item)
            if not icon_url:
                icon_url = search_coin_icon_by_name(item)
            if not icon_url:
                icon_url = get_defillama_icon(item, category)
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
        time.sleep(0.3)
    
    print(f"📊 {category}: ✓ {downloaded}, ✗ {failed}")
    return downloaded, failed

def main():
    """Основная функция."""
    print("🚀 Загружаем ВСЕ оставшиеся иконки...")
    print(f"📁 Frontend: {FRONTEND_ICONS_DIR}")
    print(f"📁 API: {API_ICONS_DIR}")
    
    total_downloaded = 0
    total_failed = 0
    
    for category, items in ALL_MISSING_ITEMS.items():
        downloaded, failed = download_icons_for_category(category, items)
        total_downloaded += downloaded
        total_failed += failed
    
    print(f"\n🎉 ИТОГО:")
    print(f"✓ Загружено: {total_downloaded}")
    print(f"✗ Не удалось: {total_failed}")
    print(f"📁 Все иконки сохранены на бекенде в: {API_ICONS_DIR}")

if __name__ == "__main__":
    main()
