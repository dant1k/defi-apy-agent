#!/usr/bin/env python3
"""
Проверка соответствия наших сетей с CoinGecko
"""

import requests
import json
import time

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

def get_coingecko_chains():
    """Получаем список сетей с CoinGecko"""
    try:
        # Используем API CoinGecko для получения списка сетей
        url = "https://api.coingecko.com/api/v3/asset_platforms"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            platforms = response.json()
            chains = []
            
            for platform in platforms:
                chain_info = {
                    "id": platform.get("id", ""),
                    "name": platform.get("name", ""),
                    "short_name": platform.get("shortname", ""),
                    "chain_identifier": platform.get("chain_identifier", ""),
                    "native_coin_id": platform.get("native_coin_id", "")
                }
                chains.append(chain_info)
            
            return chains
        else:
            print(f"Ошибка API CoinGecko: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Ошибка получения сетей CoinGecko: {e}")
        return []

def find_matches(our_chains, coingecko_chains):
    """Находим соответствия между нашими сетями и CoinGecko"""
    matches = []
    no_matches = []
    
    # Создаем словарь для быстрого поиска
    cg_dict = {}
    for chain in coingecko_chains:
        # Добавляем разные варианты названий
        cg_dict[chain["name"].lower()] = chain
        cg_dict[chain["id"].lower()] = chain
        if chain["short_name"]:
            cg_dict[chain["short_name"].lower()] = chain
        if chain["chain_identifier"]:
            cg_dict[str(chain["chain_identifier"]).lower()] = chain
    
    # Маппинг известных соответствий
    known_mappings = {
        "bsc": "binance-smart-chain",
        "mainnet": "ethereum",
        "fuel-ignition": "fuel",
        "plume mainnet": "plume",
        "starknet": "starknet"
    }
    
    for our_chain in our_chains:
        found = False
        match_info = None
        
        # Пробуем найти точное соответствие
        our_chain_lower = our_chain.lower()
        if our_chain_lower in cg_dict:
            match_info = cg_dict[our_chain_lower]
            found = True
        elif our_chain_lower in known_mappings:
            mapping = known_mappings[our_chain_lower]
            if mapping in cg_dict:
                match_info = cg_dict[mapping]
                found = True
        
        if found:
            matches.append({
                "our_name": our_chain,
                "cg_name": match_info["name"],
                "cg_id": match_info["id"],
                "cg_short": match_info["short_name"],
                "native_coin": match_info["native_coin_id"]
            })
        else:
            no_matches.append(our_chain)
    
    return matches, no_matches

def main():
    """Основная функция"""
    print("🔍 Проверяем соответствие наших сетей с CoinGecko...")
    print("=" * 60)
    
    # Получаем наши сети
    print("📡 Получаем список наших сетей...")
    our_chains = get_our_chains()
    print(f"Найдено наших сетей: {len(our_chains)}")
    
    # Получаем сети CoinGecko
    print("\n📡 Получаем список сетей CoinGecko...")
    coingecko_chains = get_coingecko_chains()
    print(f"Найдено сетей CoinGecko: {len(coingecko_chains)}")
    
    # Находим соответствия
    print("\n🔍 Ищем соответствия...")
    matches, no_matches = find_matches(our_chains, coingecko_chains)
    
    # Выводим результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"✅ Найдено соответствий: {len(matches)}")
    print(f"❌ Не найдено соответствий: {len(no_matches)}")
    print(f"📈 Покрытие: {(len(matches) * 100) // len(our_chains)}%")
    
    print(f"\n✅ НАЙДЕННЫЕ СООТВЕТСТВИЯ:")
    for match in matches:
        print(f"  {match['our_name']} -> {match['cg_name']} (id: {match['cg_id']})")
    
    if no_matches:
        print(f"\n❌ НЕ НАЙДЕНЫ СООТВЕТСТВИЯ:")
        for chain in no_matches:
            print(f"  {chain}")
    
    print(f"\n🌐 Ссылка на CoinGecko: https://www.coingecko.com/ru/chains")

if __name__ == "__main__":
    main()
