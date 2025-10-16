#!/usr/bin/env python3
"""
Скрипт для загрузки иконок токенов и протоколов через CoinGecko API
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
COINGECKO_API = "https://api.coingecko.com/api/v3"
ICONS_DIR = Path("frontend/public/icons")
TOKENS_FILE = "frontend/public/data/tokens.json"
PROTOCOLS_FILE = "frontend/public/data/protocols.json"

# Создаем директории
ICONS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.joinpath("tokens").mkdir(exist_ok=True)
ICONS_DIR.joinpath("chains").mkdir(exist_ok=True)
ICONS_DIR.joinpath("protocols").mkdir(exist_ok=True)
ICONS_DIR.parent.joinpath("data").mkdir(exist_ok=True)

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {path.name}")
            return True
    except Exception as e:
        print(f"✗ Failed {path.name}: {e}")
    return False

def get_coingecko_tokens():
    """Получить список токенов из CoinGecko"""
    try:
        # Получаем топ-200 токенов
        response = requests.get(f"{COINGECKO_API}/coins/markets", params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 200,
            "page": 1
        })
        
        if response.status_code == 200:
            tokens = response.json()
            token_data = []
            
            for token in tokens:
                symbol = token["symbol"].upper()
                name = token["name"]
                image_url = token["image"]
                
                # Скачиваем иконку
                icon_path = ICONS_DIR / "tokens" / f"{symbol}.png"
                if download_image(image_url, icon_path):
                    token_data.append({
                        "symbol": symbol,
                        "name": name,
                        "icon": f"/icons/tokens/{symbol}.png"
                    })
                
                time.sleep(0.1)  # Rate limiting
            
            # Сохраняем данные
            with open(TOKENS_FILE, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print(f"✓ Downloaded {len(token_data)} token icons")
            return token_data
            
    except Exception as e:
        print(f"✗ Error getting tokens: {e}")
    
    return []

def get_coingecko_chains():
    """Получить список сетей из CoinGecko"""
    try:
        response = requests.get(f"{COINGECKO_API}/asset_platforms")
        
        if response.status_code == 200:
            platforms = response.json()
            chain_data = []
            
            # Фильтруем популярные сети
            popular_chains = [
                "ethereum", "binance-smart-chain", "polygon-pos", "avalanche",
                "arbitrum-one", "optimistic-ethereum", "solana", "aptos",
                "sui", "base", "linea", "mantle", "fantom", "cronos"
            ]
            
            for platform in platforms:
                if platform["id"] in popular_chains:
                    name = platform["name"]
                    chain_id = platform["id"]
                    
                    # Пробуем найти иконку через поиск
                    search_response = requests.get(f"{COINGECKO_API}/search", params={
                        "query": name
                    })
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        if search_data["coins"]:
                            coin = search_data["coins"][0]
                            image_url = coin["large"]
                            
                            # Скачиваем иконку
                            icon_path = ICONS_DIR / "chains" / f"{name}.png"
                            if download_image(image_url, icon_path):
                                chain_data.append({
                                    "name": name,
                                    "id": chain_id,
                                    "icon": f"/icons/chains/{name}.png"
                                })
                    
                    time.sleep(0.2)  # Rate limiting
            
            # Сохраняем данные
            with open(PROTOCOLS_FILE, 'w') as f:
                json.dump(chain_data, f, indent=2)
            
            print(f"✓ Downloaded {len(chain_data)} chain icons")
            return chain_data
            
    except Exception as e:
        print(f"✗ Error getting chains: {e}")
    
    return []

def main():
    print("🚀 Starting icon download from CoinGecko...")
    
    # Скачиваем токены
    print("\n📱 Downloading token icons...")
    tokens = get_coingecko_tokens()
    
    # Скачиваем сети
    print("\n🌐 Downloading chain icons...")
    chains = get_coingecko_chains()
    
    print(f"\n✅ Complete! Downloaded {len(tokens)} tokens and {len(chains)} chains")
    print(f"📁 Icons saved to: {ICONS_DIR}")
    print(f"📄 Data saved to: {TOKENS_FILE}, {PROTOCOLS_FILE}")

if __name__ == "__main__":
    main()
