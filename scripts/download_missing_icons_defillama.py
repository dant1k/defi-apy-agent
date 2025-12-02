#!/usr/bin/env python3
"""
Агрессивный поиск недостающих иконок на DeFiLlama для выпадающих меню
"""

import os
import requests
import json
import time
from pathlib import Path
from urllib.parse import quote
import shutil

# Настройки
API_DIR = "api/static/icons"
FRONTEND_DIR = "frontend/public/icons"
COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFILLAMA_API = "https://defillama.com"
CMC_API = "https://pro-api.coinmarketcap.com/v1"
CMC_API_KEY = "4dc743a6ee7f4294a2d34f2969e37014"

def ensure_directories():
    """Создаем необходимые директории"""
    for category in ["chains", "protocols", "tokens"]:
        os.makedirs(f"{API_DIR}/{category}", exist_ok=True)
        os.makedirs(f"{FRONTEND_DIR}/{category}", exist_ok=True)

def get_missing_icons():
    """Получаем список недостающих иконок"""
    missing = {"chains": [], "protocols": [], "tokens": []}
    
    # Получаем активные элементы из API
    try:
        response = requests.get("http://localhost:8000/strategies?min_tvl=1000000&limit=500", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            # Собираем уникальные элементы
            chains = set()
            protocols = set()
            tokens = set()
            
            for item in items:
                if item.get("chain"):
                    chains.add(item["chain"])
                if item.get("protocol"):
                    protocols.add(item["protocol"])
                if item.get("token_pair"):
                    for token in item["token_pair"].split("-"):
                        if token.strip():
                            tokens.add(token.strip())
            
            # Проверяем какие иконки отсутствуют
            import re
            for chain in chains:
                filename = f"{re.sub(r'[^A-Z0-9]', '', chain.upper())}.png"
                if not os.path.exists(f"{API_DIR}/chains/{filename}"):
                    missing["chains"].append((chain, filename))
            
            for protocol in protocols:
                filename = f"{re.sub(r'[^A-Z0-9]', '', protocol.upper())}.png"
                if not os.path.exists(f"{API_DIR}/protocols/{filename}"):
                    missing["protocols"].append((protocol, filename))
            
            for token in tokens:
                filename = f"{token}.png"
                if not os.path.exists(f"{API_DIR}/tokens/{filename}"):
                    missing["tokens"].append((token, filename))
                    
    except Exception as e:
        print(f"Ошибка получения данных из API: {e}")
    
    return missing

def search_defillama_icon(name, category):
    """Поиск иконки на DeFiLlama"""
    try:
        # Пробуем разные варианты поиска на DeFiLlama
        search_terms = [
            name.lower(),
            name.lower().replace("-", ""),
            name.lower().replace("_", ""),
            name.lower().replace(".", ""),
        ]
        
        for term in search_terms:
            # Пробуем найти через API DeFiLlama
            if category == "protocols":
                # Поиск протоколов
                url = f"https://api.llama.fi/protocol/{term}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "logo" in data:
                        return data["logo"]
            
            elif category == "chains":
                # Поиск сетей
                url = f"https://api.llama.fi/chains"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    chains = response.json()
                    for chain in chains:
                        if (chain.get("name", "").lower() == term or 
                            chain.get("tokenSymbol", "").lower() == term):
                            return chain.get("logo")
            
            elif category == "tokens":
                # Поиск токенов через DeFiLlama
                url = f"https://coins.llama.fi/prices/current/{term}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "coins" in data:
                        for coin_id, coin_data in data["coins"].items():
                            if coin_data.get("symbol", "").lower() == term.lower():
                                return coin_data.get("logo")
        
        return None
        
    except Exception as e:
        print(f"Ошибка поиска на DeFiLlama для {name}: {e}")
        return None

def search_coingecko_icon(name, category):
    """Поиск иконки на CoinGecko"""
    try:
        if category == "tokens":
            # Поиск токенов
            search_terms = [
                name.lower(),
                name.lower().replace("-", ""),
                name.lower().replace("_", ""),
            ]
            
            for term in search_terms:
                # Поиск по символу
                url = f"{COINGECKO_API}/coins/{term}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "image" in data:
                        return data["image"]
                
                # Поиск через список
                url = f"{COINGECKO_API}/coins/list"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    coins = response.json()
                    for coin in coins:
                        if (coin.get("symbol", "").lower() == term.lower() or 
                            coin.get("id", "").lower() == term.lower()):
                            coin_id = coin["id"]
                            coin_url = f"{COINGECKO_API}/coins/{coin_id}"
                            coin_response = requests.get(coin_url, timeout=10)
                            if coin_response.status_code == 200:
                                coin_data = coin_response.json()
                                if "image" in coin_data:
                                    return coin_data["image"]
        
        return None
        
    except Exception as e:
        print(f"Ошибка поиска на CoinGecko для {name}: {e}")
        return None

def search_cmc_icon(name, category):
    """Поиск иконки на CoinMarketCap"""
    try:
        if category == "tokens":
            headers = {
                'X-CMC_PRO_API_KEY': CMC_API_KEY,
                'Accept': 'application/json'
            }
            
            # Поиск по символу
            url = f"{CMC_API}/cryptocurrency/quotes/latest"
            params = {'symbol': name.upper()}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]:
                    for coin_data in data["data"].values():
                        if "logo" in coin_data:
                            return coin_data["logo"]
        
        return None
        
    except Exception as e:
        print(f"Ошибка поиска на CMC для {name}: {e}")
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
    print("🔍 Агрессивный поиск недостающих иконок на DeFiLlama...")
    
    ensure_directories()
    missing = get_missing_icons()
    
    total_missing = sum(len(items) for items in missing.values())
    print(f"📊 Найдено {total_missing} недостающих иконок")
    
    downloaded = 0
    
    # Обрабатываем каждую категорию
    for category, items in missing.items():
        if not items:
            continue
            
        print(f"\n🔍 Загружаем иконки {category}...")
        
        for name, filename in items:
            print(f"🔍 Ищем иконку для {name}...")
            
            # Пробуем разные источники
            icon_url = None
            
            # 1. DeFiLlama
            icon_url = search_defillama_icon(name, category)
            if icon_url:
                print(f"  📍 Найдено на DeFiLlama: {icon_url}")
            
            # 2. CoinGecko (если не найдено на DeFiLlama)
            if not icon_url and category == "tokens":
                icon_url = search_coingecko_icon(name, category)
                if icon_url:
                    print(f"  📍 Найдено на CoinGecko: {icon_url}")
            
            # 3. CoinMarketCap (если не найдено)
            if not icon_url and category == "tokens":
                icon_url = search_cmc_icon(name, category)
                if icon_url:
                    print(f"  📍 Найдено на CMC: {icon_url}")
            
            # Скачиваем если найдено
            if icon_url:
                if download_icon(icon_url, filename, category):
                    print(f"  ✅ Скачано: {filename}")
                    downloaded += 1
                else:
                    print(f"  ❌ Ошибка скачивания: {filename}")
            else:
                print(f"  ❌ Не найдено: {filename}")
            
            # Небольшая пауза между запросами
            time.sleep(0.5)
    
    print(f"\n🎉 ИТОГО:")
    print(f"✅ Загружено: {downloaded}")
    print(f"❌ Не удалось: {total_missing - downloaded}")
    print(f"📁 Все иконки сохранены на бекенде в: {API_DIR}")

if __name__ == "__main__":
    main()
