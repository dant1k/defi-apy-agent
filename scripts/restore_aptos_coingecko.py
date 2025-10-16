#!/usr/bin/env python3
"""
Скрипт для восстановления Aptos через CoinGecko
"""

import os
import requests
from pathlib import Path

# Настройки
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

def restore_aptos_from_coingecko():
    """Восстановить Aptos через CoinGecko"""
    print("🔄 Restoring Aptos from CoinGecko...")
    
    try:
        # Ищем Aptos в CoinGecko
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": "aptos"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                for coin in data["coins"]:
                    coin_name = coin.get("name", "").lower()
                    if "aptos" in coin_name:
                        logo_url = coin.get("large", "")
                        if logo_url:
                            backup_path = BACKUP_DIR / "chains" / "Aptos.png"
                            if download_image(logo_url, backup_path):
                                print(f"✅ Restored Aptos from CoinGecko: {coin.get('name')}")
                                return True
            
            print(f"❌ Aptos not found in CoinGecko")
            return False
        else:
            print(f"❌ Failed to search CoinGecko")
            return False
            
    except Exception as e:
        print(f"❌ Error restoring Aptos from CoinGecko: {e}")
        return False

def main():
    print("🚀 Restoring Aptos from CoinGecko...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    if restore_aptos_from_coingecko():
        print(f"✅ Successfully restored Aptos!")
    else:
        print(f"❌ Failed to restore Aptos")

if __name__ == "__main__":
    main()

