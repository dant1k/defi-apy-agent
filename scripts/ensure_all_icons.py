#!/usr/bin/env python3
"""
Скрипт для обеспечения иконками всех элементов в выпадающих меню
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL"""
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
    """Получить URL иконки из CoinGecko по gecko_id"""
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except:
        pass
    return ""

def search_coin_icon_by_name(name: str) -> str:
    """Поиск иконки по имени в CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": name
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                coin = data["coins"][0]
                return coin.get("large", "")
    except:
        pass
    return ""

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def ensure_chain_icons():
    """Обеспечить иконками все сети"""
    print("🌐 Ensuring chain icons...")
    
    # Получаем список всех сетей из API
    try:
        response = requests.get("http://localhost:8000/chains")
        if response.status_code == 200:
            chains = response.json().get("items", [])
        else:
            print("❌ Failed to get chains from API")
            return
    except:
        print("❌ API not available, using fallback chains")
        chains = ["Ethereum", "Bitcoin", "Arbitrum", "Base", "Polygon", "Avalanche", "Solana", "Aptos", "Sui", "Linea", "Mantle", "Fantom", "Cronos", "Harmony", "Aurora", "Celo", "Kava", "Moonbeam", "Moonriver", "Astar", "Klaytn", "Flow", "Near", "Algorand", "Cosmos", "Polkadot", "Cardano", "Tron"]
    
    downloaded = 0
    for chain in chains:
        file_name = normalize_name(chain)
        local_path = ICONS_DIR / "chains" / f"{file_name}.png"
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Проверяем, есть ли иконка локально или в backup
        if local_path.exists() or backup_path.exists():
            continue
            
        print(f"🔍 Looking for icon: {chain}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(chain)
        
        if icon_url:
            # Скачиваем в backup (так как это не популярная сеть)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new chain icons")

def ensure_token_icons():
    """Обеспечить иконками все токены"""
    print("🪙 Ensuring token icons...")
    
    # Получаем список токенов из API
    try:
        response = requests.get("http://localhost:8000/tokens?limit=100")
        if response.status_code == 200:
            tokens_data = response.json().get("tokens", [])
            tokens = [token.get("symbol", "") for token in tokens_data if token.get("symbol")]
        else:
            print("❌ Failed to get tokens from API")
            return
    except:
        print("❌ API not available, using fallback tokens")
        tokens = ["BTC", "ETH", "USDT", "BNB", "XRP", "SOL", "USDC", "STETH", "TRX", "DOGE", "ADA", "WSTETH", "WBETH", "WBTC", "LINK", "USDE", "WEETH", "XLM", "BCH", "HYPE", "SUI", "WETH", "AVAX", "LEO", "USDS", "HBAR", "LTC", "SHIB", "MNT", "XMR", "TON", "CRO", "DOT", "DAI", "UNI", "TAO", "ZEC", "OKB", "AAVE", "PEPE", "NEAR", "ETC", "APT", "ONDO", "WLD", "POL", "ICP", "ARB", "ALGO", "ATOM"]
    
    downloaded = 0
    for token in tokens:
        if not token:
            continue
            
        local_path = ICONS_DIR / "tokens" / f"{token}.png"
        backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
        
        # Проверяем, есть ли иконка локально или в backup
        if local_path.exists() or backup_path.exists():
            continue
            
        print(f"🔍 Looking for icon: {token}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(token)
        
        if icon_url:
            # Скачиваем в backup
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new token icons")

def ensure_protocol_icons():
    """Обеспечить иконками все протоколы"""
    print("🏛️ Ensuring protocol icons...")
    
    # Получаем список протоколов из API
    try:
        response = requests.get("http://localhost:8000/protocols")
        if response.status_code == 200:
            protocols = response.json().get("items", [])
        else:
            print("❌ Failed to get protocols from API")
            return
    except:
        print("❌ API not available, using fallback protocols")
        protocols = ["AAVE", "Compound", "Uniswap", "Curve", "Maker", "Lido", "Pendle", "SparkLend", "Morpho", "EigenLayer", "Binance", "OKX", "Bitfinex", "Bybit", "Robinhood", "Gemini", "Gate", "Coinbase", "HTX", "KuCoin", "JustLend", "Hyperliquid", "Base", "Arbitrum", "Optimism", "Polygon", "Avalanche", "Solana", "Aptos", "Sui", "Linea", "Mantle", "Fantom", "Cronos", "Harmony", "Aurora", "Celo", "Kava", "Moonbeam", "Moonriver", "Astar", "Klaytn", "Flow", "Near", "Algorand", "Cosmos", "Polkadot", "Cardano", "Tron"]
    
    downloaded = 0
    for protocol in protocols:
        file_name = normalize_name(protocol).upper()
        local_path = ICONS_DIR / "protocols" / f"{file_name}.png"
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Проверяем, есть ли иконка локально или в backup
        if local_path.exists() or backup_path.exists():
            continue
            
        print(f"🔍 Looking for icon: {protocol}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(protocol)
        
        if icon_url:
            # Скачиваем в backup
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new protocol icons")

def main():
    print("🚀 Ensuring all dropdown menu items have icons...")
    
    # Создаем директории
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Обеспечиваем иконки для всех категорий
    ensure_chain_icons()
    ensure_token_icons()
    ensure_protocol_icons()
    
    print("\n✅ Icon coverage complete!")
    print("All dropdown menu items should now have icons available.")

if __name__ == "__main__":
    main()

