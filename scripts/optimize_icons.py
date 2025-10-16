#!/usr/bin/env python3
"""
Скрипт для оптимизации иконок - оставляем только популярные локально
"""

import os
import json
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

# Популярные токены (топ-50 по market cap)
POPULAR_TOKENS = [
    "BTC", "ETH", "USDT", "BNB", "XRP", "SOL", "USDC", "STETH", "TRX", "DOGE",
    "ADA", "WSTETH", "WBETH", "WBTC", "LINK", "USDE", "WEETH", "XLM", "BCH", "HYPE",
    "SUI", "WETH", "AVAX", "LEO", "USDS", "HBAR", "LTC", "SHIB", "MNT", "XMR",
    "TON", "CRO", "DOT", "DAI", "UNI", "TAO", "ZEC", "OKB", "AAVE", "PEPE",
    "NEAR", "ETC", "APT", "ONDO", "WLD", "POL", "ICP", "ARB", "ALGO", "ATOM"
]

# Популярные сети (топ-30)
POPULAR_CHAINS = [
    "Ethereum", "Binance", "Polygon", "Avalanche", "Arbitrum", "Optimism", 
    "Base", "Solana", "Aptos", "Sui", "Linea", "Mantle", "Fantom", "Cronos",
    "Harmony", "Aurora", "Celo", "Kava", "Moonbeam", "Moonriver", "Astar",
    "Klaytn", "Flow", "Near", "Algorand", "Cosmos", "Polkadot", "Cardano",
    "Tron", "Bitcoin"
]

# Популярные протоколы (топ-50)
POPULAR_PROTOCOLS = [
    "AAVE", "COMPOUND", "UNISWAP", "CURVE", "MAKER", "LIDO", "PENDLE", "SPARKLEND",
    "MORPHO", "EIGENLAYER", "BINANCECEX", "OKX", "BITFINEX", "BYBIT", "ROBINHOOD",
    "GEMINI", "GATE", "COINBASEBRIDGE", "BINANCEBITCOIN", "USDT0", "MORPHOV1",
    "BABYLONPROTOCOL", "HTX", "SKYLENDING", "ARBITRUMBRIDGE", "BITMEX", "BITGET",
    "DERIBIT", "MEXC", "KUCOIN", "JUSTLEND", "HYPERLIQUIDBRIDGE", "JUSTCRYPTOS",
    "BASEBRIDGE", "WBTC", "ETHENAUSDE", "ETHERFISTAKE", "BINANCESTAKEDETH", "PENDLE",
    "SPARKLEND", "MORPHO", "EIGENLAYER", "BINANCECEX", "OKX", "BITFINEX", "BYBIT",
    "ROBINHOOD", "GEMINI", "GATE", "COINBASEBRIDGE"
]

def move_to_backup(category: str, keep_list: list):
    """Переместить неиспользуемые иконки в backup"""
    category_dir = ICONS_DIR / category
    backup_category_dir = BACKUP_DIR / category
    
    if not category_dir.exists():
        return
    
    # Создаем backup директорию
    backup_category_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    kept_count = 0
    
    for icon_file in category_dir.glob("*.png"):
        icon_name = icon_file.stem  # имя без расширения
        
        if icon_name in keep_list:
            kept_count += 1
            print(f"✓ Keeping: {category}/{icon_name}.png")
        else:
            # Перемещаем в backup
            backup_path = backup_category_dir / icon_file.name
            icon_file.rename(backup_path)
            moved_count += 1
            print(f"→ Moved to backup: {category}/{icon_name}.png")
    
    print(f"📁 {category}: kept {kept_count}, moved {moved_count} to backup")
    return kept_count, moved_count

def create_backend_endpoint():
    """Создать endpoint для загрузки иконок через бек"""
    endpoint_code = '''
@app.get("/icons/{category}/{filename}")
async def get_icon(category: str, filename: str):
    """Получить иконку из backup или скачать из CoinGecko"""
    icon_path = f"api/static/icons/{category}/{filename}"
    
    # Если есть локально - отдаем
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/png")
    
    # Иначе скачиваем из CoinGecko (можно добавить логику)
    return {"error": "Icon not found"}
'''
    
    with open("api/icon_endpoint.py", "w") as f:
        f.write(endpoint_code)
    
    print("📄 Created api/icon_endpoint.py")

def main():
    print("🚀 Optimizing icons - keeping only popular ones locally...")
    
    # Создаем backup директорию
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_kept = 0
    total_moved = 0
    
    # Оптимизируем токены
    print("\n📱 Optimizing tokens...")
    kept, moved = move_to_backup("tokens", POPULAR_TOKENS)
    total_kept += kept
    total_moved += moved
    
    # Оптимизируем сети
    print("\n🌐 Optimizing chains...")
    kept, moved = move_to_backup("chains", POPULAR_CHAINS)
    total_kept += kept
    total_moved += moved
    
    # Оптимизируем протоколы
    print("\n🏛️ Optimizing protocols...")
    kept, moved = move_to_backup("protocols", POPULAR_PROTOCOLS)
    total_kept += kept
    total_moved += moved
    
    # Создаем endpoint для бекенда
    create_backend_endpoint()
    
    # Показываем статистику
    print(f"\n✅ Optimization complete!")
    print(f"📊 Kept {total_kept} popular icons locally")
    print(f"📦 Moved {total_moved} icons to backup")
    print(f"💾 Backup location: {BACKUP_DIR}")
    print(f"🌐 Backend endpoint: /icons/{{category}}/{{filename}}")

if __name__ == "__main__":
    main()

