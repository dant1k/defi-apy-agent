#!/usr/bin/env python3
"""
Загружает иконки сетей из DeFiLlama API.
"""

import os
import requests
from pathlib import Path

# Настройки
FRONTEND_ICONS_DIR = Path("frontend/public/icons/chains")
API_ICONS_DIR = Path("api/static/icons/chains")

# Маппинг названий к DeFiLlama
DEFILLAMA_CHAIN_MAPPING = {
    "ARBITRUM": "arbitrum",
    "BSC": "bsc", 
    "CORE": "core",
    "FLARE": "flare",
    "FLOW": "flow",
    "FRAXTAL": "fraxtal",
    "FUEL": "fuel",
    "HEMI": "hemi",
    "HYPERLIQUID": "hyperliquid",
    "MAINNET": "ethereum",
    "MULTIVERSX": "multiversx",
    "NEO": "neo",
    "OSMOSIS": "osmosis",
    "STARKNET": "starknet",
    "STELLAR": "stellar",
    "TON": "ton"
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

def get_defillama_chain_icon(chain_id: str) -> str:
    """Получить URL иконки из DeFiLlama."""
    try:
        # Пробуем получить данные о сети
        response = requests.get(f"https://api.llama.fi/chains")
        if response.status_code == 200:
            chains = response.json()
            for chain in chains:
                if chain.get("id") == chain_id or chain.get("name", "").lower() == chain_id.lower():
                    return f"https://icons.llama.fi/{chain_id}.png"
    except:
        pass
    return f"https://icons.llama.fi/{chain_id}.png"

def download_defillama_chain_icons():
    """Загружает иконки из DeFiLlama."""
    print("🔍 Загружаем иконки из DeFiLlama...")
    
    downloaded = 0
    failed = 0
    
    for chain_name, chain_id in DEFILLAMA_CHAIN_MAPPING.items():
        icon_file = f"{chain_name}.png"
        
        frontend_path = FRONTEND_ICONS_DIR / icon_file
        api_path = API_ICONS_DIR / icon_file
        
        # Пропускаем если уже есть
        if frontend_path.exists() and api_path.exists():
            print(f"✓ {chain_name} - уже есть")
            continue
        
        print(f"🔍 Загружаем {chain_name} ({chain_id})...")
        
        # Получаем URL иконки
        icon_url = get_defillama_chain_icon(chain_id)
        
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
    
    print(f"\n📊 Результат:")
    print(f"✓ Загружено: {downloaded}")
    print(f"✗ Не удалось: {failed}")

if __name__ == "__main__":
    download_defillama_chain_icons()

