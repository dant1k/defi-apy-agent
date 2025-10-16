#!/usr/bin/env python3
"""
Исправление недостающих иконок в выпадающих меню
"""

import os
import requests
import json
import time
from pathlib import Path
import shutil
import re

# Настройки
API_DIR = "api/static/icons"
FRONTEND_DIR = "frontend/public/icons"
COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFILLAMA_API = "https://api.llama.fi"
CMC_API = "https://pro-api.coinmarketcap.com/v1"
CMC_API_KEY = "4dc743a6ee7f4294a2d34f2969e37014"

def ensure_directories():
    """Создаем необходимые директории"""
    for category in ["chains", "protocols", "tokens"]:
        os.makedirs(f"{API_DIR}/{category}", exist_ok=True)
        os.makedirs(f"{FRONTEND_DIR}/{category}", exist_ok=True)

def get_dropdown_missing_icons():
    """Получаем список недостающих иконок для выпадающих меню"""
    missing = {"protocols": [], "tokens": []}
    
    try:
        response = requests.get("http://localhost:8000/strategies?min_tvl=1000000&limit=500", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            # Собираем уникальные элементы
            protocols = set()
            tokens = set()
            
            for item in items:
                if item.get("protocol"):
                    protocols.add(item["protocol"])
                if item.get("token_pair"):
                    for token in item["token_pair"].split("-"):
                        if token.strip():
                            tokens.add(token.strip())
            
            # Проверяем недостающие протоколы
            missing_protocols = [
                "astroport",
                "silo-v2", 
                "sushiswap-v3"
            ]
            
            for protocol in missing_protocols:
                if protocol in protocols:
                    filename = f"{re.sub(r'[^A-Z0-9]', '', protocol.upper())}.png"
                    if not os.path.exists(f"{API_DIR}/protocols/{filename}"):
                        missing["protocols"].append((protocol, filename))
            
            # Проверяем недостающие токены (первые 20 самых важных)
            important_tokens = [
                "$MYRO", "20261231", "4", "40AVAX", "80RZR", "9SUSDC",
                "ACRV", "AI16Z", "AIDAUSDC", "AIDAUSDT", "ATONE", "BNEO",
                "CUSDX", "DYFI", "EPENDLE", "ESFDX", "FBEETS", "FRAX",
                "FRAXBP", "FRXUSD", "FTM", "FUEL", "FXRP", "FXS"
            ]
            
            for token in important_tokens:
                if token in tokens:
                    filename = f"{token}.png"
                    if not os.path.exists(f"{API_DIR}/tokens/{filename}"):
                        missing["tokens"].append((token, filename))
                        
    except Exception as e:
        print(f"Ошибка получения данных из API: {e}")
    
    return missing

def search_protocol_icon(protocol_name):
    """Поиск иконки протокола"""
    try:
        # 1. DeFiLlama протоколы
        url = f"{DEFILLAMA_API}/protocol/{protocol_name.lower().replace('-', '')}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "logo" in data:
                return data["logo"]
        
        # 2. DeFiLlama список всех протоколов
        url = f"{DEFILLAMA_API}/protocols"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            protocols = response.json()
            for protocol in protocols:
                if (protocol.get("name", "").lower() == protocol_name.lower() or
                    protocol.get("slug", "").lower() == protocol_name.lower()):
                    return protocol.get("logo")
        
        # 3. Прямой поиск по известным URL
        known_protocols = {
            "astroport": "https://assets.astroport.fi/tokens/astroport.png",
            "silo-v2": "https://raw.githubusercontent.com/silo-finance/brand-kit/main/silo-logo.png",
            "sushiswap-v3": "https://raw.githubusercontent.com/sushiswap/icons/master/token/sushi.png"
        }
        
        if protocol_name.lower() in known_protocols:
            return known_protocols[protocol_name.lower()]
        
        return None
        
    except Exception as e:
        print(f"Ошибка поиска протокола {protocol_name}: {e}")
        return None

def search_token_icon(token_symbol):
    """Поиск иконки токена"""
    try:
        # 1. CoinGecko по символу
        url = f"{COINGECKO_API}/coins/{token_symbol.lower()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "image" in data:
                return data["image"]
        
        # 2. CoinGecko поиск по списку
        url = f"{COINGECKO_API}/coins/list"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            coins = response.json()
            for coin in coins:
                if coin.get("symbol", "").upper() == token_symbol.upper():
                    coin_id = coin["id"]
                    coin_url = f"{COINGECKO_API}/coins/{coin_id}"
                    coin_response = requests.get(coin_url, timeout=10)
                    if coin_response.status_code == 200:
                        coin_data = coin_response.json()
                        if "image" in coin_data:
                            return coin_data["image"]
        
        # 3. DeFiLlama токены
        url = f"https://coins.llama.fi/prices/current/{token_symbol.lower()}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "coins" in data:
                for coin_id, coin_data in data["coins"].items():
                    if coin_data.get("symbol", "").upper() == token_symbol.upper():
                        return coin_data.get("logo")
        
        # 4. CoinMarketCap
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }
        url = f"{CMC_API}/cryptocurrency/quotes/latest"
        params = {'symbol': token_symbol.upper()}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and data["data"]:
                for coin_data in data["data"].values():
                    if "logo" in coin_data:
                        return coin_data["logo"]
        
        return None
        
    except Exception as e:
        print(f"Ошибка поиска токена {token_symbol}: {e}")
        return None

def download_icon(url, filename, category):
    """Скачиваем иконку"""
    try:
        if not url or not url.startswith(('http://', 'https://')):
            return False
            
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            # Сохраняем в API
            api_path = f"{API_DIR}/{category}/{filename}"
            with open(api_path, 'wb') as f:
                f.write(response.content)
            
            # Копируем в frontend
            frontend_path = f"{FRONTEND_DIR}/{category}/{filename}"
            shutil.copy2(api_path, frontend_path)
            
            return True
    except Exception as e:
        print(f"Ошибка скачивания {url}: {e}")
    
    return False

def main():
    """Основная функция"""
    print("🔧 Исправляем недостающие иконки в выпадающих меню...")
    
    ensure_directories()
    missing = get_dropdown_missing_icons()
    
    total_missing = len(missing["protocols"]) + len(missing["tokens"])
    print(f"📊 Найдено {total_missing} недостающих иконок для выпадающих меню")
    
    downloaded = 0
    
    # Обрабатываем протоколы
    if missing["protocols"]:
        print(f"\n🔍 Загружаем иконки протоколов...")
        for name, filename in missing["protocols"]:
            print(f"🔍 Ищем иконку для протокола {name}...")
            
            icon_url = search_protocol_icon(name)
            if icon_url:
                print(f"  📍 Найдено: {icon_url}")
                if download_icon(icon_url, filename, "protocols"):
                    print(f"  ✅ Скачано: {filename}")
                    downloaded += 1
                else:
                    print(f"  ❌ Ошибка скачивания: {filename}")
            else:
                print(f"  ❌ Не найдено: {filename}")
            
            time.sleep(1)
    
    # Обрабатываем токены
    if missing["tokens"]:
        print(f"\n🔍 Загружаем иконки токенов...")
        for name, filename in missing["tokens"]:
            print(f"🔍 Ищем иконку для токена {name}...")
            
            icon_url = search_token_icon(name)
            if icon_url:
                print(f"  📍 Найдено: {icon_url}")
                if download_icon(icon_url, filename, "tokens"):
                    print(f"  ✅ Скачано: {filename}")
                    downloaded += 1
                else:
                    print(f"  ❌ Ошибка скачивания: {filename}")
            else:
                print(f"  ❌ Не найдено: {filename}")
            
            time.sleep(1)
    
    print(f"\n🎉 ИТОГО:")
    print(f"✅ Загружено: {downloaded}")
    print(f"❌ Не удалось: {total_missing - downloaded}")
    print(f"📁 Все иконки сохранены на бекенде в: {API_DIR}")

if __name__ == "__main__":
    main()
