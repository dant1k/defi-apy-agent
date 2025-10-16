#!/usr/bin/env python3
"""
Загружает недостающие иконки сетей с CoinGecko и других источников.
"""

import os
import requests
import json
from pathlib import Path

# Настройки
FRONTEND_ICONS_DIR = Path("frontend/public/icons/chains")
API_ICONS_DIR = Path("api/static/icons/chains")

# Создаем директории
FRONTEND_ICONS_DIR.mkdir(parents=True, exist_ok=True)
API_ICONS_DIR.mkdir(parents=True, exist_ok=True)

# Недостающие сети
MISSING_CHAINS = [
    "Aptos", "Arbitrum", "BSC", "Core", "Filecoin", "Flare", "Flow", "Fraxtal",
    "Fuel-ignition", "Hemi", "Hyperliquid", "Mainnet", "MultiversX", "Neo",
    "Osmosis", "Starknet", "Stellar", "Ton"
]

# Маппинг названий сетей к CoinGecko ID
CHAIN_MAPPING = {
    "Aptos": "aptos",
    "Arbitrum": "arbitrum-one",
    "BSC": "binance-smart-chain",
    "Core": "core-dao",
    "Filecoin": "filecoin",
    "Flare": "flare",
    "Flow": "flow",
    "Fraxtal": "fraxtal",
    "Fuel-ignition": "fuel",
    "Hemi": "hemi",
    "Hyperliquid": "hyperliquid",
    "Mainnet": "ethereum",
    "MultiversX": "multiversx",
    "Neo": "neo",
    "Osmosis": "osmosis",
    "Starknet": "starknet",
    "Stellar": "stellar",
    "Ton": "the-open-network"
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

def download_chain_icons():
    """Загружает иконки для недостающих сетей."""
    print("🔍 Загружаем иконки недостающих сетей...")
    
    downloaded = 0
    failed = 0
    
    for chain in MISSING_CHAINS:
        normalized_name = chain.upper().replace(" ", "").replace("-", "")
        icon_file = f"{normalized_name}.png"
        
        frontend_path = FRONTEND_ICONS_DIR / icon_file
        api_path = API_ICONS_DIR / icon_file
        
        # Пропускаем если уже есть
        if frontend_path.exists() and api_path.exists():
            print(f"✓ {chain} - уже есть")
            continue
        
        print(f"🔍 Ищем иконку для {chain}...")
        
        # Пробуем CoinGecko
        gecko_id = CHAIN_MAPPING.get(chain)
        if gecko_id:
            icon_url = get_coin_icon_from_gecko(gecko_id)
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
                continue
        
        print(f"✗ Не удалось найти иконку для {chain}")
        failed += 1
    
    print(f"\n📊 Результат:")
    print(f"✓ Загружено: {downloaded}")
    print(f"✗ Не удалось: {failed}")
    print(f"📁 Frontend: {FRONTEND_ICONS_DIR}")
    print(f"📁 API: {API_ICONS_DIR}")

if __name__ == "__main__":
    download_chain_icons()

