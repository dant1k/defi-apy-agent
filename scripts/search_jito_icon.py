#!/usr/bin/env python3
"""
Скрипт для поиска иконки JITO токена через поиск CoinGecko
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

def search_jito_in_coingecko():
    """Поиск JITO в CoinGecko"""
    try:
        # Пробуем разные варианты поиска
        search_terms = ["jito", "JITO", "Jito"]
        
        for term in search_terms:
            print(f"🔍 Searching for: {term}")
            response = requests.get("https://api.coingecko.com/api/v3/search", params={
                "query": term
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("coins"):
                    for coin in data["coins"]:
                        coin_name = coin.get("name", "").lower()
                        coin_symbol = coin.get("symbol", "").upper()
                        
                        print(f"  → Found: {coin.get('name')} ({coin_symbol})")
                        
                        # Ищем точное совпадение
                        if "jito" in coin_name or coin_symbol == "JITO":
                            print(f"  → Match found: {coin.get('name')} ({coin_symbol})")
                            return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error searching JITO in CoinGecko: {e}")
    return ""

def get_jito_icon_direct():
    """Прямое получение иконки JITO"""
    try:
        # Пробуем разные ID
        jito_ids = ["jito", "jito-governance-token", "jito-sol"]
        
        for jito_id in jito_ids:
            print(f"🔍 Trying ID: {jito_id}")
            response = requests.get(f"https://api.coingecko.com/api/v3/coins/{jito_id}")
            if response.status_code == 200:
                data = response.json()
                icon_url = data.get("image", {}).get("large", "")
                if icon_url:
                    print(f"  → Found icon for ID: {jito_id}")
                    return icon_url
        
        return ""
    except Exception as e:
        print(f"Error getting JITO icon directly: {e}")
    return ""

def main():
    print("🚀 Searching for JITO token icon...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Стратегия 1: Поиск в CoinGecko
    print("🔍 Strategy 1: Search in CoinGecko...")
    icon_url = search_jito_in_coingecko()
    
    # Стратегия 2: Прямое получение
    if not icon_url:
        print("🔍 Strategy 2: Direct ID lookup...")
        icon_url = get_jito_icon_direct()
    
    if icon_url:
        print(f"✅ Found JITO icon: {icon_url}")
        
        # Скачиваем иконку для протокола jito-liquid-staking
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', "jito-liquid-staking".upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        if download_image(icon_url, backup_path):
            print("✅ JITO icon downloaded successfully!")
        else:
            print("❌ Failed to download JITO icon")
    else:
        print("❌ JITO icon not found")
    
    print("\n🎉 JITO icon search complete!")

if __name__ == "__main__":
    main()

