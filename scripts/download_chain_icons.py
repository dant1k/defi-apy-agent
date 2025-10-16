#!/usr/bin/env python3
"""
Скрипт для загрузки иконок сетей из разных источников
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons/chains")
CHAINS_FILE = "frontend/public/data/chains.json"

# Создаем директории
ICONS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.parent.parent.joinpath("data").mkdir(exist_ok=True)

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

def get_defillama_chains():
    """Получить список сетей из DeFiLlama"""
    try:
        response = requests.get("https://api.llama.fi/chains")
        
        if response.status_code == 200:
            chains = response.json()
            chain_data = []
            
            for chain in chains:
                name = chain.get("name", "")
                tokenSymbol = chain.get("tokenSymbol", "")
                logo = chain.get("logo", "")
                
                if name and logo:
                    # Нормализуем имя для файла
                    file_name = name.replace(" ", "").replace("-", "").replace("_", "")
                    
                    # Скачиваем иконку
                    icon_path = ICONS_DIR / f"{file_name}.png"
                    if download_image(logo, icon_path):
                        chain_data.append({
                            "name": name,
                            "symbol": tokenSymbol,
                            "icon": f"/icons/chains/{file_name}.png",
                            "logo_url": logo
                        })
                
                time.sleep(0.1)  # Rate limiting
            
            print(f"✓ Downloaded {len(chain_data)} chain icons from DeFiLlama")
            return chain_data
            
    except Exception as e:
        print(f"✗ Error getting chains from DeFiLlama: {e}")
    
    return []

def get_coingecko_chains():
    """Получить популярные сети из CoinGecko"""
    try:
        # Получаем asset platforms
        response = requests.get("https://api.coingecko.com/api/v3/asset_platforms")
        
        if response.status_code == 200:
            platforms = response.json()
            chain_data = []
            
            # Фильтруем популярные сети
            popular_chains = [
                "ethereum", "binance-smart-chain", "polygon-pos", "avalanche",
                "arbitrum-one", "optimistic-ethereum", "solana", "aptos",
                "sui", "base", "linea", "mantle", "fantom", "cronos",
                "ton", "near", "algorand", "cosmos", "polkadot", "cardano",
                "tron", "stellar", "litecoin", "bitcoin-cash", "dogecoin"
            ]
            
            for platform in platforms:
                if platform["id"] in popular_chains:
                    name = platform["name"]
                    chain_id = platform["id"]
                    
                    # Пробуем найти иконку через поиск
                    search_response = requests.get("https://api.coingecko.com/api/v3/search", params={
                        "query": name
                    })
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        if search_data["coins"]:
                            coin = search_data["coins"][0]
                            image_url = coin["large"]
                            
                            # Нормализуем имя для файла
                            file_name = name.replace(" ", "").replace("-", "").replace("_", "")
                            
                            # Скачиваем иконку
                            icon_path = ICONS_DIR / f"{file_name}.png"
                            if download_image(image_url, icon_path):
                                chain_data.append({
                                    "name": name,
                                    "id": chain_id,
                                    "icon": f"/icons/chains/{file_name}.png",
                                    "logo_url": image_url
                                })
                    
                    time.sleep(0.2)  # Rate limiting
            
            print(f"✓ Downloaded {len(chain_data)} chain icons from CoinGecko")
            return chain_data
            
    except Exception as e:
        print(f"✗ Error getting chains from CoinGecko: {e}")
    
    return []

def main():
    print("🚀 Starting chain icon download...")
    
    # Скачиваем из DeFiLlama
    print("\n🌐 Downloading from DeFiLlama...")
    defillama_chains = get_defillama_chains()
    
    # Скачиваем из CoinGecko
    print("\n📱 Downloading from CoinGecko...")
    coingecko_chains = get_coingecko_chains()
    
    # Объединяем результаты
    all_chains = defillama_chains + coingecko_chains
    
    # Убираем дубликаты по имени
    unique_chains = []
    seen_names = set()
    for chain in all_chains:
        if chain["name"] not in seen_names:
            unique_chains.append(chain)
            seen_names.add(chain["name"])
    
    # Сохраняем данные
    with open(CHAINS_FILE, 'w') as f:
        json.dump(unique_chains, f, indent=2)
    
    print(f"\n✅ Complete! Downloaded {len(unique_chains)} unique chain icons")
    print(f"📁 Icons saved to: {ICONS_DIR}")
    print(f"📄 Data saved to: {CHAINS_FILE}")

if __name__ == "__main__":
    main()

