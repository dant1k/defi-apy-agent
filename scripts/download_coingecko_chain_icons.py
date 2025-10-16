#!/usr/bin/env python3
"""
Загрузка иконок сетей с CoinGecko
"""

import requests
import os
import shutil
import time
from typing import Dict, List, Any

API_STATIC_DIR = "api/static/icons"
FRONTEND_PUBLIC_DIR = "frontend/public/icons"

def get_coingecko_chain_icon_url(chain_id: str) -> str:
    """Получаем URL иконки сети с CoinGecko"""
    return f"https://assets.coingecko.com/coins/images/1/large/{chain_id}.png"

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

def get_our_chains_with_coingecko_mapping() -> Dict[str, str]:
    """Получаем маппинг наших сетей на CoinGecko"""
    return {
        "Aptos": "aptos",
        "Arbitrum": "arbitrum-one", 
        "Avalanche": "avalanche",
        "BSC": "binance-smart-chain",
        "Base": "base",
        "Berachain": "berachain",
        "Cardano": "cardano",
        "Celo": "celo",
        "Core": "core",
        "Cronos": "cronos",
        "Ethereum": "ethereum",
        "Etherlink": "etherlink",
        "Fantom": "fantom",
        "Filecoin": "filecoin",
        "Flow": "flow",
        "Fraxtal": "fraxtal",
        "Fuel-ignition": "fuel-ignition",
        "Hemi": "hemi",
        "Hyperliquid": "hyperliquid",
        "Linea": "linea",
        "Mainnet": "ethereum",  # Mainnet это Ethereum
        "MultiversX": "elrond",
        "Neo": "neo",
        "Optimism": "optimistic-ethereum",
        "Osmosis": "osmosis",
        "Plasma": "plasma",
        "Polkadot": "polkadot",
        "Solana": "solana",
        "Sonic": "sonic",
        "Starknet": "starknet",
        "Stellar": "stellar",
        "Sui": "sui",
        "Ton": "the-open-network"
    }

def normalize_chain_name(chain_name: str) -> str:
    """Нормализуем имя сети для файла"""
    return chain_name.upper().replace(" ", "").replace("-", "").replace(".", "")

def main():
    """Основная функция"""
    print("🚀 Загружаем иконки сетей с CoinGecko...")
    print("=" * 50)
    
    # Создаем директории
    os.makedirs(os.path.join(API_STATIC_DIR, "chains"), exist_ok=True)
    os.makedirs(os.path.join(FRONTEND_PUBLIC_DIR, "chains"), exist_ok=True)
    
    # Получаем маппинг
    chain_mapping = get_our_chains_with_coingecko_mapping()
    
    downloaded_count = 0
    failed_count = 0
    
    for our_chain, cg_id in chain_mapping.items():
        print(f"\n🔍 Обрабатываем {our_chain} -> {cg_id}")
        
        # Нормализуем имя для файла
        filename = f"{normalize_chain_name(our_chain)}.png"
        api_path = os.path.join(API_STATIC_DIR, "chains", filename)
        frontend_path = os.path.join(FRONTEND_PUBLIC_DIR, "chains", filename)
        
        # Проверяем, есть ли уже файл
        if os.path.exists(api_path):
            print(f"  ✅ {our_chain} - уже есть")
            # Копируем на фронтенд если нужно
            if not os.path.exists(frontend_path):
                shutil.copy(api_path, frontend_path)
                print(f"  📋 Скопировано на фронтенд")
            continue
        
        # Пробуем разные варианты URL
        urls_to_try = [
            f"https://assets.coingecko.com/coins/images/1/large/{cg_id}.png",
            f"https://assets.coingecko.com/coins/images/1/small/{cg_id}.png",
            f"https://assets.coingecko.com/coins/images/1/{cg_id}.png",
            f"https://assets.coingecko.com/coins/images/{cg_id}.png"
        ]
        
        success = False
        for url in urls_to_try:
            print(f"  🔗 Пробуем: {url}")
            if download_icon(url, api_path):
                print(f"  ✅ Загружено: {filename}")
                # Копируем на фронтенд
                shutil.copy(api_path, frontend_path)
                print(f"  📋 Скопировано на фронтенд")
                downloaded_count += 1
                success = True
                break
            time.sleep(0.5)  # Небольшая пауза между запросами
        
        if not success:
            print(f"  ❌ Не удалось загрузить: {our_chain}")
            failed_count += 1
    
    print(f"\n🎉 ИТОГИ:")
    print(f"✅ Загружено: {downloaded_count}")
    print(f"❌ Не удалось: {failed_count}")
    print(f"📁 Иконки сохранены в: {API_STATIC_DIR}/chains")
    print(f"📁 Иконки скопированы в: {FRONTEND_PUBLIC_DIR}/chains")

if __name__ == "__main__":
    main()
