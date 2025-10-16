#!/usr/bin/env python3
"""
Загружает иконки сетей из альтернативных источников.
"""

import os
import requests
from pathlib import Path

# Настройки
FRONTEND_ICONS_DIR = Path("frontend/public/icons/chains")
API_ICONS_DIR = Path("api/static/icons/chains")

# Альтернативные источники иконок
CHAIN_ICON_SOURCES = {
    "ARBITRUM": "https://cryptologos.cc/logos/arbitrum-arb-logo.png",
    "BSC": "https://cryptologos.cc/logos/bnb-bnb-logo.png", 
    "CORE": "https://cryptologos.cc/logos/core-coredao-logo.png",
    "FLARE": "https://cryptologos.cc/logos/flare-flr-logo.png",
    "FLOW": "https://cryptologos.cc/logos/flow-flow-logo.png",
    "FRAXTAL": "https://cryptologos.cc/logos/frax-frax-logo.png",
    "FUEL": "https://cryptologos.cc/logos/fuel-fuel-logo.png",
    "HEMI": "https://cryptologos.cc/logos/hemi-hemi-logo.png",
    "HYPERLIQUID": "https://cryptologos.cc/logos/hyperliquid-hyperliquid-logo.png",
    "MAINNET": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
    "MULTIVERSX": "https://cryptologos.cc/logos/multiversx-egld-logo.png",
    "NEO": "https://cryptologos.cc/logos/neo-neo-logo.png",
    "OSMOSIS": "https://cryptologos.cc/logos/osmosis-osmo-logo.png",
    "STARKNET": "https://cryptologos.cc/logos/starknet-stark-logo.png",
    "STELLAR": "https://cryptologos.cc/logos/stellar-xlm-logo.png",
    "TON": "https://cryptologos.cc/logos/toncoin-ton-logo.png"
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

def download_alternative_chain_icons():
    """Загружает иконки из альтернативных источников."""
    print("🔍 Загружаем иконки из альтернативных источников...")
    
    downloaded = 0
    failed = 0
    
    for chain_name, icon_url in CHAIN_ICON_SOURCES.items():
        icon_file = f"{chain_name}.png"
        
        frontend_path = FRONTEND_ICONS_DIR / icon_file
        api_path = API_ICONS_DIR / icon_file
        
        # Пропускаем если уже есть
        if frontend_path.exists() and api_path.exists():
            print(f"✓ {chain_name} - уже есть")
            continue
        
        print(f"🔍 Загружаем {chain_name}...")
        
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
    download_alternative_chain_icons()

