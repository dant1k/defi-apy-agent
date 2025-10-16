#!/usr/bin/env python3
"""
Скрипт для скачивания недостающих иконок
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
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

def get_coin_icon_from_gecko(gecko_id: str) -> str:
    """Получить URL иконки из CoinGecko по gecko_id"""
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{gecko_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get("image", {}).get("large", "")
    except:
        pass
    return ""

def search_coin_icon_by_name(name: str) -> str:
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

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def download_missing_chains():
    """Скачать недостающие иконки сетей"""
    print("🌐 Downloading missing chain icons...")
    
    # Получаем список недостающих сетей
    missing_chains = [
        "Berachain", "Bifrost", "Bifrost Network", "Bitcoincash", "Bitlayer", "Bob", "Boba", "Bsquared", 
        "Carbon", "Chiliz", "Conflux", "Core", "Cronos_zkevm", "Defichain", "Echelon_initia", "Filecoin", 
        "Flare", "Flow", "Fraxtal", "Fuel-ignition", "Gnosis", "Gravity", "Hemi", "Hyperevm", "Hyperliquid", 
        "ICP", "IOTA EVM", "Icp", "Karura", "Kava", "Klaytn", "Kusama", "Libre", "Lisk", "Litecoin", 
        "Mainnet", "Manta", "Mixin", "Mode", "Moonbeam", "Moonriver", "Morph", "Move", "Movement", 
        "MultiversX", "Neo", "Neutron", "Nolus", "Obyte", "Ontology", "Op_bnb", "Opbnb", "Optimism", 
        "Persistence", "Plume Mainnet", "Polynomial", "Rollux", "Rootstock", "Scroll", "Sei", "Stacks", 
        "Starknet", "Swell", "Tac", "Taiko", "Telos", "Tezos", "Unichain", "Unit0", "Venom", "Xdc", 
        "Zksync", "avax", "berachain", "canto", "emerald", "fraxtal", "fuse", "gnosis", "hyperevm", 
        "kava", "mode", "moonbeam", "moonriver", "one", "optimism", "real", "rootstock", "scroll", 
        "sei", "zkevm", "zksync"
    ]
    
    downloaded = 0
    for chain in missing_chains:
        file_name = normalize_name(chain)
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
            
        print(f"🔍 Looking for icon: {chain}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(chain)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new chain icons")

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
            
        print(f"🔍 Looking for icon: {token}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(token)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new token icons")

def download_missing_protocols():
    """Скачать недостающие иконки протоколов"""
    print("\n🏛️ Downloading missing protocol icons...")
    
    missing_protocols = [
        "full-sail", "gammaswap-yield-tokens", "impermax-v2", "jito-liquid-staking", 
        "lista-lending", "moonwell-lending"
    ]
    
    downloaded = 0
    for protocol in missing_protocols:
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
            
        print(f"🔍 Looking for icon: {protocol}")
        
        # Пробуем найти через CoinGecko
        icon_url = search_coin_icon_by_name(protocol)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        
        time.sleep(0.1)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new protocol icons")

def main():
    print("🚀 Downloading missing icons for dropdown menus...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем недостающие иконки
    download_missing_chains()
    download_missing_tokens()
    download_missing_protocols()
    
    print("\n✅ Missing icons download complete!")
    print("All dropdown menu items should now have icons available.")

if __name__ == "__main__":
    main()

