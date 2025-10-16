#!/usr/bin/env python3
"""
Скрипт для загрузки ВСЕХ иконок сетей из DeFiLlama
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons/chains")
CHAINS_FILE = "frontend/public/data/all_chains.json"

# Создаем директории
ICONS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.parent.parent.joinpath("data").mkdir(exist_ok=True)

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL"""
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
    """Получить URL иконки из CoinGecko по gecko_id"""
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except:
        pass
    return ""

def get_all_defillama_chains():
    """Получить ВСЕ сети из DeFiLlama"""
    try:
        print("🌐 Fetching all chains from DeFiLlama...")
        response = requests.get("https://api.llama.fi/chains")
        
        if response.status_code == 200:
            chains = response.json()
            chain_data = []
            downloaded_count = 0
            
            print(f"Found {len(chains)} chains total")
            
            for i, chain in enumerate(chains, 1):
                name = chain.get("name", "")
                tokenSymbol = chain.get("tokenSymbol", "")
                gecko_id = chain.get("gecko_id", "")
                
                print(f"[{i}/{len(chains)}] Processing: {name}")
                
                if name and gecko_id:
                    # Получаем иконку из CoinGecko
                    logo_url = get_coin_icon_from_gecko(gecko_id)
                    
                    if logo_url:
                        # Нормализуем имя для файла
                        file_name = name.replace(" ", "").replace("-", "").replace("_", "")
                        file_name = "".join(c for c in file_name if c.isalnum())
                        
                        # Скачиваем иконку
                        icon_path = ICONS_DIR / f"{file_name}.png"
                        if download_image(logo_url, icon_path):
                            chain_data.append({
                                "name": name,
                                "symbol": tokenSymbol,
                                "icon": f"/icons/chains/{file_name}.png",
                                "logo_url": logo_url,
                                "chain_id": chain.get("chainId"),
                                "gecko_id": gecko_id
                            })
                            downloaded_count += 1
                
                # Rate limiting
                time.sleep(0.2)
                
                # Показываем прогресс каждые 50
                if i % 50 == 0:
                    print(f"Progress: {i}/{len(chains)} chains processed, {downloaded_count} icons downloaded")
            
            # Сохраняем данные
            with open(CHAINS_FILE, 'w') as f:
                json.dump(chain_data, f, indent=2)
            
            print(f"\n✅ Complete! Downloaded {downloaded_count} chain icons from {len(chains)} total chains")
            print(f"📁 Icons saved to: {ICONS_DIR}")
            print(f"📄 Data saved to: {CHAINS_FILE}")
            
            return chain_data
            
    except Exception as e:
        print(f"✗ Error getting chains from DeFiLlama: {e}")
    
    return []

def main():
    print("🚀 Starting COMPLETE chain icon download from DeFiLlama...")
    print("⚠️  This will download ALL available chain icons (may take a while)")
    
    # Скачиваем все сети
    chains = get_all_defillama_chains()
    
    if chains:
        print(f"\n🎉 Successfully downloaded {len(chains)} chain icons!")
        print("Now you have comprehensive chain icon coverage for your DeFi app!")
    else:
        print("\n❌ Failed to download chain icons")

if __name__ == "__main__":
    main()
