#!/usr/bin/env python3
"""
Скрипт для скачивания иконки JITO токена
"""

import os
import requests
import json
import time
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

def get_jito_icon_from_coingecko():
    """Получить иконку JITO из CoinGecko"""
    try:
        # Используем ID из URL: jito
        response = requests.get("https://api.coingecko.com/api/v3/coins/jito")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except Exception as e:
        print(f"Error getting JITO icon from CoinGecko: {e}")
    return ""

def main():
    print("🚀 Downloading JITO token icon...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Получаем иконку JITO
    print("🔍 Getting JITO icon from CoinGecko...")
    icon_url = get_jito_icon_from_coingecko()
    
    if icon_url:
        print(f"  → Found JITO icon: {icon_url}")
        
        # Скачиваем иконку для протокола jito-liquid-staking
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', "jito-liquid-staking".upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        if download_image(icon_url, backup_path):
            print("✅ JITO icon downloaded successfully!")
        else:
            print("❌ Failed to download JITO icon")
    else:
        print("❌ JITO icon not found in CoinGecko")
    
    print("\n🎉 JITO icon download complete!")

if __name__ == "__main__":
    main()

