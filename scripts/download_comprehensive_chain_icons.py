#!/usr/bin/env python3
"""
Комплексный скрипт для загрузки иконок сетей из разных источников
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons/chains")
CHAINS_FILE = "frontend/public/data/comprehensive_chains.json"

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

def get_defillama_chains():
    """Получить все сети из DeFiLlama"""
    try:
        print("🌐 Fetching all chains from DeFiLlama...")
        response = requests.get("https://api.llama.fi/chains")
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"✗ Error getting chains from DeFiLlama: {e}")
    
    return []

def download_comprehensive_chain_icons():
    """Комплексная загрузка иконок сетей"""
    chains = get_defillama_chains()
    if not chains:
        return []
    
    chain_data = []
    downloaded_count = 0
    
    print(f"Found {len(chains)} chains total")
    
    for i, chain in enumerate(chains, 1):
        name = chain.get("name", "")
        tokenSymbol = chain.get("tokenSymbol", "")
        gecko_id = chain.get("gecko_id", "")
        
        print(f"[{i}/{len(chains)}] Processing: {name}")
        
        if not name:
            continue
            
        # Нормализуем имя для файла
        file_name = name.replace(" ", "").replace("-", "").replace("_", "")
        file_name = "".join(c for c in file_name if c.isalnum())
        
        # Проверяем, есть ли уже иконка
        icon_path = ICONS_DIR / f"{file_name}.png"
        if icon_path.exists():
            print(f"  → Already exists: {file_name}.png")
            chain_data.append({
                "name": name,
                "symbol": tokenSymbol,
                "icon": f"/icons/chains/{file_name}.png",
                "chain_id": chain.get("chainId"),
                "gecko_id": gecko_id
            })
            continue
        
        logo_url = ""
        
        # Метод 1: Пробуем через gecko_id
        if gecko_id:
            logo_url = get_coin_icon_from_gecko(gecko_id)
            if logo_url:
                print(f"  → Found via gecko_id: {gecko_id}")
        
        # Метод 2: Поиск по имени
        if not logo_url:
            logo_url = search_coin_icon_by_name(name)
            if logo_url:
                print(f"  → Found via name search: {name}")
        
        # Метод 3: Поиск по символу токена
        if not logo_url and tokenSymbol:
            logo_url = search_coin_icon_by_name(tokenSymbol)
            if logo_url:
                print(f"  → Found via token symbol: {tokenSymbol}")
        
        # Скачиваем иконку
        if logo_url and download_image(logo_url, icon_path):
            chain_data.append({
                "name": name,
                "symbol": tokenSymbol,
                "icon": f"/icons/chains/{file_name}.png",
                "logo_url": logo_url,
                "chain_id": chain.get("chainId"),
                "gecko_id": gecko_id
            })
            downloaded_count += 1
        else:
            print(f"  → No icon found for: {name}")
        
        # Rate limiting
        time.sleep(0.15)
        
        # Показываем прогресс каждые 50
        if i % 50 == 0:
            print(f"Progress: {i}/{len(chains)} chains processed, {downloaded_count} new icons downloaded")
    
    # Сохраняем данные
    with open(CHAINS_FILE, 'w') as f:
        json.dump(chain_data, f, indent=2)
    
    print(f"\n✅ Complete! Downloaded {downloaded_count} new chain icons from {len(chains)} total chains")
    print(f"📁 Total icons in directory: {len(list(ICONS_DIR.glob('*.png')))}")
    print(f"📄 Data saved to: {CHAINS_FILE}")
    
    return chain_data

def main():
    print("🚀 Starting COMPREHENSIVE chain icon download...")
    print("🔍 Using multiple methods: gecko_id, name search, token symbol search")
    
    chains = download_comprehensive_chain_icons()
    
    if chains:
        print(f"\n🎉 Successfully processed {len(chains)} chains!")
        print("Now you have comprehensive chain icon coverage for your DeFi app!")
    else:
        print("\n❌ Failed to download chain icons")

if __name__ == "__main__":
    main()

