#!/usr/bin/env python3
"""
Загрузка иконок сетей с DeFiLlama
"""

import requests
import os
import shutil
import time
import json
from typing import Dict, List, Any

API_STATIC_DIR = "api/static/icons"
FRONTEND_PUBLIC_DIR = "frontend/public/icons"

def get_defillama_chains():
    """Получаем список сетей с DeFiLlama"""
    try:
        # Используем API DeFiLlama для получения списка сетей
        url = "https://api.llama.fi/chains"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            chains = response.json()
            return chains
        else:
            print(f"Ошибка API DeFiLlama: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Ошибка получения сетей DeFiLlama: {e}")
        return []

def get_our_chains():
    """Получаем список наших сетей"""
    try:
        response = requests.get("http://localhost:8000/strategies?min_tvl=1000000&limit=500", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            chains = set()
            for item in items:
                if item.get("chain"):
                    chains.add(item["chain"])
            
            return sorted(list(chains))
    except Exception as e:
        print(f"Ошибка получения наших сетей: {e}")
        return []

def find_defillama_matches(our_chains, defillama_chains):
    """Находим соответствия между нашими сетями и DeFiLlama"""
    matches = []
    no_matches = []
    
    # Создаем словарь для быстрого поиска
    dl_dict = {}
    for chain in defillama_chains:
        # Добавляем разные варианты названий
        dl_dict[chain["name"].lower()] = chain
        if chain.get("gecko_id"):
            dl_dict[chain["gecko_id"].lower()] = chain
        if chain.get("tokenSymbol"):
            dl_dict[chain["tokenSymbol"].lower()] = chain
    
    # Маппинг известных соответствий
    known_mappings = {
        "bsc": "bsc",
        "mainnet": "ethereum",
        "fuel-ignition": "fuel",
        "plume mainnet": "plume",
        "starknet": "starknet",
        "multiversx": "elrond",
        "optimism": "optimism",
        "arbitrum": "arbitrum",
        "polygon": "polygon",
        "avalanche": "avalanche",
        "solana": "solana",
        "ethereum": "ethereum",
        "base": "base",
        "fantom": "fantom",
        "celo": "celo",
        "cardano": "cardano",
        "polkadot": "polkadot",
        "cosmos": "cosmos",
        "osmosis": "osmosis",
        "sui": "sui",
        "aptos": "aptos",
        "ton": "ton",
        "stellar": "stellar",
        "neo": "neo",
        "flow": "flow",
        "filecoin": "filecoin",
        "cronos": "cronos",
        "linea": "linea",
        "berachain": "berachain",
        "core": "core",
        "fraxtal": "fraxtal",
        "etherlink": "etherlink",
        "hemi": "hemi",
        "hyperliquid": "hyperliquid",
        "plasma": "plasma",
        "sonic": "sonic",
        "flare": "flare",
        "sei": "sei"
    }
    
    for our_chain in our_chains:
        found = False
        match_info = None
        
        # Пробуем найти точное соответствие
        our_chain_lower = our_chain.lower()
        if our_chain_lower in dl_dict:
            match_info = dl_dict[our_chain_lower]
            found = True
        elif our_chain_lower in known_mappings:
            mapping = known_mappings[our_chain_lower]
            if mapping in dl_dict:
                match_info = dl_dict[mapping]
                found = True
        
        if found:
            # Используем gecko_id для иконки, если есть, иначе name
            icon_id = match_info.get("gecko_id") or match_info["name"].lower().replace(" ", "-")
            matches.append({
                "our_name": our_chain,
                "dl_name": match_info["name"],
                "dl_gecko_id": match_info.get("gecko_id", ""),
                "dl_token_symbol": match_info.get("tokenSymbol", ""),
                "icon_url": f"https://icons.llama.fi/{icon_id}.png"
            })
        else:
            no_matches.append(our_chain)
    
    return matches, no_matches

def download_icon(url: str, save_path: str) -> bool:
    """Загружаем иконку"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        return True
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return False

def normalize_chain_name(chain_name: str) -> str:
    """Нормализуем имя сети для файла"""
    return chain_name.upper().replace(" ", "").replace("-", "").replace(".", "")

def main():
    """Основная функция"""
    print("🚀 Загружаем иконки сетей с DeFiLlama...")
    print("=" * 60)
    
    # Создаем директории
    os.makedirs(os.path.join(API_STATIC_DIR, "chains"), exist_ok=True)
    os.makedirs(os.path.join(FRONTEND_PUBLIC_DIR, "chains"), exist_ok=True)
    
    # Получаем наши сети
    print("📡 Получаем список наших сетей...")
    our_chains = get_our_chains()
    print(f"Найдено наших сетей: {len(our_chains)}")
    
    # Получаем сети DeFiLlama
    print("\n📡 Получаем список сетей DeFiLlama...")
    defillama_chains = get_defillama_chains()
    print(f"Найдено сетей DeFiLlama: {len(defillama_chains)}")
    
    # Находим соответствия
    print("\n🔍 Ищем соответствия...")
    matches, no_matches = find_defillama_matches(our_chains, defillama_chains)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ СООТВЕТСТВИЙ:")
    print(f"✅ Найдено соответствий: {len(matches)}")
    print(f"❌ Не найдено соответствий: {len(no_matches)}")
    print(f"📈 Покрытие: {(len(matches) * 100) // len(our_chains)}%")
    
    if no_matches:
        print(f"\n❌ НЕ НАЙДЕНЫ СООТВЕТСТВИЯ:")
        for chain in no_matches:
            print(f"  {chain}")
    
    # Загружаем иконки
    print(f"\n🔄 ЗАГРУЖАЕМ ИКОНКИ:")
    downloaded_count = 0
    failed_count = 0
    
    for match in matches:
        our_chain = match["our_name"]
        icon_url = match["icon_url"]
        
        print(f"\n🔍 Обрабатываем {our_chain} -> {match['dl_name']}")
        print(f"  🔗 URL: {icon_url}")
        
        # Нормализуем имя для файла
        filename = f"{normalize_chain_name(our_chain)}.png"
        api_path = os.path.join(API_STATIC_DIR, "chains", filename)
        frontend_path = os.path.join(FRONTEND_PUBLIC_DIR, "chains", filename)
        
        # Загружаем иконку
        if download_icon(icon_url, api_path):
            print(f"  ✅ Загружено: {filename}")
            # Копируем на фронтенд
            shutil.copy(api_path, frontend_path)
            print(f"  📋 Скопировано на фронтенд")
            downloaded_count += 1
        else:
            print(f"  ❌ Не удалось загрузить: {our_chain}")
            failed_count += 1
        
        time.sleep(0.5)  # Пауза между запросами
    
    print(f"\n🎉 ИТОГИ ЗАГРУЗКИ:")
    print(f"✅ Загружено: {downloaded_count}")
    print(f"❌ Не удалось: {failed_count}")
    print(f"📁 Иконки сохранены в: {API_STATIC_DIR}/chains")
    print(f"📁 Иконки скопированы в: {FRONTEND_PUBLIC_DIR}/chains")

if __name__ == "__main__":
    main()
