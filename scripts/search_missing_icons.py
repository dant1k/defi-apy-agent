#!/usr/bin/env python3
"""
Скрипт для поиска недостающих иконок в DeFiLlama и CoinMarketCap
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

def search_defillama_chains():
    """Поиск иконок сетей в DeFiLlama"""
    print("🌐 Searching DeFiLlama for chain icons...")
    
    try:
        response = requests.get("https://api.llama.fi/chains")
        if response.status_code == 200:
            chains = response.json()
            print(f"Found {len(chains)} chains in DeFiLlama")
            return chains
        else:
            print("❌ Failed to get chains from DeFiLlama")
            return []
    except Exception as e:
        print(f"❌ Error getting chains from DeFiLlama: {e}")
        return []

def search_defillama_protocols():
    """Поиск иконок протоколов в DeFiLlama"""
    print("🏛️ Searching DeFiLlama for protocol icons...")
    
    try:
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            protocols = response.json()
            print(f"Found {len(protocols)} protocols in DeFiLlama")
            return protocols
        else:
            print("❌ Failed to get protocols from DeFiLlama")
            return []
    except Exception as e:
        print(f"❌ Error getting protocols from DeFiLlama: {e}")
        return []

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

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def download_missing_chains_from_defillama():
    """Скачать недостающие иконки сетей из DeFiLlama"""
    print("🌐 Downloading missing chain icons from DeFiLlama...")
    
    # Список недостающих сетей
    missing_chains = [
        "Bifrost Network", "Bitcoincash", "Bob", "Boba", "Bsquared", "Carbon", "Chiliz", 
        "Conflux", "Core", "Cronos_zkevm", "Defichain", "Echelon_initia", "Filecoin", 
        "Flare", "Flow", "Fraxtal", "Fuel-ignition", "Gravity", "Hemi", "Hyperliquid", 
        "IOTA EVM", "Karura", "Klaytn", "Kusama", "Libre", "Moonriver", "Morph", "Move", 
        "Movement", "MultiversX", "Neo", "Neutron", "Nolus", "Obyte", "Ontology", 
        "Op_bnb", "Opbnb", "Optimism", "Persistence", "Plume Mainnet", "Polynomial", 
        "Rollux", "Rootstock", "Scroll", "Sei", "Stacks", "Starknet", "Swell", "Tac", 
        "Taiko", "Telos", "Tezos", "Unichain", "Unit0", "Venom", "Xdc", "Zksync", 
        "avax", "canto", "emerald", "fraxtal", "fuse", "moonriver", "one", "optimism", 
        "real", "rootstock", "scroll", "sei", "zkevm", "zksync"
    ]
    
    # Получаем данные из DeFiLlama
    defillama_chains = search_defillama_chains()
    
    downloaded = 0
    for chain in missing_chains:
        file_name = normalize_name(chain)
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
            
        print(f"🔍 Looking for: {chain}")
        
        # Ищем в DeFiLlama по имени
        icon_url = ""
        for dl_chain in defillama_chains:
            if dl_chain.get("name", "").lower() == chain.lower():
                gecko_id = dl_chain.get("gecko_id", "")
                if gecko_id:
                    icon_url = search_coingecko_by_id(gecko_id)
                    if icon_url:
                        print(f"  → Found via DeFiLlama gecko_id: {gecko_id}")
                        break
        
        # Если не нашли в DeFiLlama, пробуем CoinGecko напрямую
        if not icon_url:
            icon_url = search_coingecko_by_name(chain)
            if icon_url:
                print(f"  → Found via CoinGecko search")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new chain icons from DeFiLlama/CoinGecko")

def download_missing_protocols_from_defillama():
    """Скачать недостающие иконки протоколов из DeFiLlama"""
    print("\n🏛️ Downloading missing protocol icons from DeFiLlama...")
    
    # Список недостающих протоколов
    missing_protocols = [
        "full-sail", "gammaswap-yield-tokens", "impermax-v2", "jito-liquid-staking", 
        "lista-lending", "moonwell-lending"
    ]
    
    # Получаем данные из DeFiLlama
    defillama_protocols = search_defillama_protocols()
    
    downloaded = 0
    for protocol in missing_protocols:
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
            
        print(f"🔍 Looking for: {protocol}")
        
        # Ищем в DeFiLlama по имени
        icon_url = ""
        for dl_protocol in defillama_protocols:
            if dl_protocol.get("name", "").lower() == protocol.lower():
                gecko_id = dl_protocol.get("gecko_id", "")
                if gecko_id:
                    icon_url = search_coingecko_by_id(gecko_id)
                    if icon_url:
                        print(f"  → Found via DeFiLlama gecko_id: {gecko_id}")
                        break
        
        # Если не нашли в DeFiLlama, пробуем CoinGecko напрямую
        if not icon_url:
            icon_url = search_coingecko_by_name(protocol)
            if icon_url:
                print(f"  → Found via CoinGecko search")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new protocol icons from DeFiLlama/CoinGecko")

def download_missing_tokens():
    """Скачать недостающие иконки токенов"""
    print("\n🪙 Downloading missing token icons...")
    
    missing_tokens = ["DEXE"]
    
    downloaded = 0
    for token in missing_tokens:
        backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
            
        print(f"🔍 Looking for: {token}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coingecko_by_name(token)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.2)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new token icons")

def main():
    print("🚀 Searching for missing icons in DeFiLlama and CoinMarketCap...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем недостающие иконки
    download_missing_chains_from_defillama()
    download_missing_protocols_from_defillama()
    download_missing_tokens()
    
    print("\n✅ Missing icons search complete!")
    print("Check the results and run coverage check again.")

if __name__ == "__main__":
    main()

