#!/usr/bin/env python3
"""
Агрессивный поиск недостающих иконок с множественными стратегиями
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

def search_coingecko_by_name(name: str) -> str:
    """Поиск иконки по имени в CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": name
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                coin = data["coins"][0]
                return coin.get("large", "")
    except:
        pass
    return ""

def search_coingecko_by_id(gecko_id: str) -> str:
    """Поиск иконки по gecko_id в CoinGecko"""
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except:
        pass
    return ""

def search_coingecko_by_symbol(symbol: str) -> str:
    """Поиск иконки по символу в CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": symbol
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                for coin in data["coins"]:
                    if coin.get("symbol", "").upper() == symbol.upper():
                        return coin.get("large", "")
    except:
        pass
    return ""

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def aggressive_search_chain(chain_name: str) -> str:
    """Агрессивный поиск иконки для сети"""
    print(f"🔍 Aggressive search for: {chain_name}")
    
    # Стратегия 1: Прямой поиск по имени
    icon_url = search_coingecko_by_name(chain_name)
    if icon_url:
        print(f"  → Found via name search")
        return icon_url
    
    # Стратегия 2: Поиск по нормализованному имени
    normalized = chain_name.replace(" ", "").replace("-", "").replace("_", "")
    if normalized != chain_name:
        icon_url = search_coingecko_by_name(normalized)
        if icon_url:
            print(f"  → Found via normalized name")
            return icon_url
    
    # Стратегия 3: Поиск по частям имени
    parts = chain_name.split()
    for part in parts:
        if len(part) > 3:  # Игнорируем короткие части
            icon_url = search_coingecko_by_name(part)
            if icon_url:
                print(f"  → Found via part: {part}")
                return icon_url
    
    # Стратегия 4: Поиск по символу (если есть)
    if len(chain_name) <= 5:  # Возможно это символ
        icon_url = search_coingecko_by_symbol(chain_name)
        if icon_url:
            print(f"  → Found via symbol search")
            return icon_url
    
    # Стратегия 5: Поиск по альтернативным названиям
    alternatives = {
        "Bitcoincash": "Bitcoin Cash",
        "Cronos_zkevm": "Cronos",
        "Defichain": "DeFiChain",
        "Echelon_initia": "Initia",
        "Fuel-ignition": "Fuel",
        "IOTA EVM": "IOTA",
        "Op_bnb": "BNB Chain",
        "Opbnb": "BNB Chain",
        "Plume Mainnet": "Plume",
        "avax": "Avalanche",
        "canto": "Canto",
        "emerald": "Emerald",
        "fraxtal": "Fraxtal",
        "fuse": "Fuse",
        "moonriver": "Moonriver",
        "one": "Harmony",
        "optimism": "Optimism",
        "real": "Real",
        "rootstock": "Rootstock",
        "scroll": "Scroll",
        "sei": "Sei",
        "zkevm": "zkEVM",
        "zksync": "zkSync"
    }
    
    if chain_name in alternatives:
        alt_name = alternatives[chain_name]
        icon_url = search_coingecko_by_name(alt_name)
        if icon_url:
            print(f"  → Found via alternative: {alt_name}")
            return icon_url
    
    print(f"  → No icon found")
    return ""

def download_remaining_chains():
    """Скачать оставшиеся иконки сетей"""
    print("🌐 Aggressive search for remaining chain icons...")
    
    # Оставшиеся сети без иконок
    remaining_chains = [
        "Chiliz", "Conflux", "Core", "Cronos_zkevm", "Defichain", "Echelon_initia", 
        "Filecoin", "Flare", "Flow", "Fraxtal", "Fuel-ignition", "Gravity", "Hemi", 
        "Hyperliquid", "IOTA EVM", "Karura", "Klaytn", "Kusama", "Libre", "Moonriver", 
        "Morph", "Move", "Movement", "MultiversX", "Neo", "Neutron", "Nolus", "Obyte", 
        "Ontology", "Op_bnb", "Opbnb", "Optimism", "Persistence", "Plume Mainnet", 
        "Polynomial", "Rollux", "Rootstock", "Scroll", "Sei", "Stacks", "Starknet", 
        "Swell", "Tac", "Taiko", "Telos", "Tezos", "avax", "canto", "emerald", 
        "fraxtal", "fuse", "moonriver", "one", "optimism", "real", "rootstock", 
        "scroll", "sei", "zkevm", "zksync"
    ]
    
    downloaded = 0
    for chain in remaining_chains:
        file_name = normalize_name(chain)
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        icon_url = aggressive_search_chain(chain)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new chain icons with aggressive search")

def download_remaining_tokens():
    """Скачать оставшиеся иконки токенов"""
    print("\n🪙 Aggressive search for remaining token icons...")
    
    remaining_tokens = ["DEXE"]
    
    downloaded = 0
    for token in remaining_tokens:
        backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Aggressive search for token: {token}")
        
        # Пробуем разные стратегии поиска
        icon_url = search_coingecko_by_name(token)
        if not icon_url:
            icon_url = search_coingecko_by_symbol(token)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new token icons with aggressive search")

def download_remaining_protocols():
    """Скачать оставшиеся иконки протоколов"""
    print("\n🏛️ Aggressive search for remaining protocol icons...")
    
    remaining_protocols = [
        "full-sail", "gammaswap-yield-tokens", "impermax-v2", "jito-liquid-staking", 
        "lista-lending", "moonwell-lending"
    ]
    
    downloaded = 0
    for protocol in remaining_protocols:
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Aggressive search for protocol: {protocol}")
        
        # Пробуем разные стратегии поиска
        icon_url = search_coingecko_by_name(protocol)
        if not icon_url:
            # Пробуем без дефисов
            clean_name = protocol.replace("-", " ")
            icon_url = search_coingecko_by_name(clean_name)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.3)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new protocol icons with aggressive search")

def main():
    print("🚀 Aggressive search for remaining missing icons...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем оставшиеся иконки
    download_remaining_chains()
    download_remaining_tokens()
    download_remaining_protocols()
    
    print("\n✅ Aggressive search complete!")
    print("Check the results and run coverage check again.")

if __name__ == "__main__":
    main()

