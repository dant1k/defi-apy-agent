#!/usr/bin/env python3
"""
Скрипт для поиска недостающих иконок через CoinMarketCap API
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
BACKUP_DIR = Path("api/static/icons")
CMC_API_KEY = "4dc743a6ee7f4294a2d34f2969e37014"

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

def search_cmc_by_symbol(symbol: str) -> str:
    """Поиск иконки по символу в CoinMarketCap"""
    try:
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }
        
        response = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            headers=headers,
            params={'symbol': symbol}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and symbol in data['data']:
                coin_data = data['data'][symbol]
                # CMC не предоставляет прямые URL иконок, но мы можем использовать их CDN
                coin_id = coin_data.get('id')
                if coin_id:
                    # CMC использует формат: https://s2.coinmarketcap.com/static/img/coins/64x64/{id}.png
                    return f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png"
    except Exception as e:
        print(f"  → CMC API error for {symbol}: {e}")
    return ""

def search_cmc_by_name(name: str) -> str:
    """Поиск иконки по имени в CoinMarketCap"""
    try:
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }
        
        response = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            headers=headers,
            params={'slug': name.lower().replace(' ', '-')}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                # Получаем первый результат
                coin_data = list(data['data'].values())[0]
                coin_id = coin_data.get('id')
                if coin_id:
                    return f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png"
    except Exception as e:
        print(f"  → CMC API error for {name}: {e}")
    return ""

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def get_chain_native_tokens():
    """Маппинг сетей к их нативным токенам"""
    return {
        "Filecoin": "FIL",
        "Flare": "FLR", 
        "Flow": "FLOW",
        "Fraxtal": "FXTL",
        "Fuel-ignition": "FUEL",
        "Gravity": "GRAV",
        "Hemi": "HEMI",
        "Hyperliquid": "HYPE",
        "IOTA EVM": "IOTA",
        "Karura": "KAR",
        "Klaytn": "KLAY",
        "Kusama": "KSM",
        "Libre": "LIBRE",
        "Moonriver": "MOVR",
        "Morph": "MORPH",
        "Move": "MOVE",
        "Movement": "MOV",
        "MultiversX": "EGLD",
        "Neo": "NEO",
        "Neutron": "NTRN",
        "Nolus": "NLS",
        "Obyte": "GBYTE",
        "Ontology": "ONT",
        "Op_bnb": "BNB",
        "Opbnb": "BNB",
        "Optimism": "OP",
        "Persistence": "XPRT",
        "Polynomial": "POLY",
        "Scroll": "SCR",
        "Sei": "SEI",
        "Stacks": "STX",
        "Starknet": "STRK",
        "Swell": "SWELL",
        "Tac": "TAC",
        "Taiko": "TKO",
        "Telos": "TLOS",
        "Tezos": "XTZ",
        "avax": "AVAX",
        "canto": "CANTO",
        "emerald": "EMD",
        "fraxtal": "FXTL",
        "fuse": "FUSE",
        "moonriver": "MOVR",
        "one": "ONE",
        "optimism": "OP",
        "real": "REAL",
        "rootstock": "RBTC",
        "scroll": "SCR",
        "sei": "SEI",
        "zkevm": "ETH",
        "zksync": "ZK"
    }

def download_remaining_chains_via_cmc():
    """Скачать оставшиеся иконки сетей через CMC"""
    print("🌐 Searching remaining chain icons via CoinMarketCap...")
    
    # Оставшиеся сети без иконок
    remaining_chains = [
        "Echelon_initia", "Filecoin", "Flare", "Flow", "Fraxtal", "Fuel-ignition", 
        "Gravity", "Hemi", "Hyperliquid", "IOTA EVM", "Karura", "Klaytn", "Kusama", 
        "Libre", "Moonriver", "Morph", "Move", "Movement", "MultiversX", "Neo", 
        "Neutron", "Nolus", "Obyte", "Ontology", "Op_bnb", "Opbnb", "Optimism", 
        "Persistence", "Polynomial", "Scroll", "Sei", "Stacks", "Starknet", "Swell", 
        "Tac", "Taiko", "Telos", "Tezos", "avax", "canto", "emerald", "fraxtal", 
        "fuse", "moonriver", "one", "optimism", "real", "rootstock", "scroll", 
        "sei", "zkevm", "zksync"
    ]
    
    native_tokens = get_chain_native_tokens()
    
    downloaded = 0
    for chain in remaining_chains:
        file_name = normalize_name(chain)
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Searching CMC for: {chain}")
        
        icon_url = ""
        
        # Стратегия 1: Поиск по нативному токену
        if chain in native_tokens:
            token_symbol = native_tokens[chain]
            print(f"  → Trying native token: {token_symbol}")
            icon_url = search_cmc_by_symbol(token_symbol)
            if icon_url:
                print(f"  → Found via native token: {token_symbol}")
        
        # Стратегия 2: Поиск по имени сети
        if not icon_url:
            icon_url = search_cmc_by_name(chain)
            if icon_url:
                print(f"  → Found via chain name")
        
        # Стратегия 3: Поиск по нормализованному имени
        if not icon_url:
            normalized = chain.replace(" ", "").replace("-", "").replace("_", "")
            if normalized != chain:
                icon_url = search_cmc_by_name(normalized)
                if icon_url:
                    print(f"  → Found via normalized name")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        else:
            print(f"  → No icon found in CMC")
        
        time.sleep(0.5)  # Rate limiting для CMC API
    
    print(f"✓ Downloaded {downloaded} new chain icons via CMC")

def download_remaining_tokens_via_cmc():
    """Скачать оставшиеся иконки токенов через CMC"""
    print("\n🪙 Searching remaining token icons via CoinMarketCap...")
    
    remaining_tokens = ["DEXE"]
    
    downloaded = 0
    for token in remaining_tokens:
        backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Searching CMC for token: {token}")
        
        icon_url = search_cmc_by_symbol(token)
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
                print(f"  → Found via CMC")
        else:
            print(f"  → No icon found in CMC")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new token icons via CMC")

def download_remaining_protocols_via_cmc():
    """Скачать оставшиеся иконки протоколов через CMC"""
    print("\n🏛️ Searching remaining protocol icons via CoinMarketCap...")
    
    remaining_protocols = [
        "full-sail", "gammaswap-yield-tokens", "impermax-v2", "jito-liquid-staking", 
        "lista-lending", "moonwell-lending"
    ]
    
    # Маппинг протоколов к их токенам
    protocol_tokens = {
        "full-sail": "SAIL",
        "gammaswap-yield-tokens": "GAMMA",
        "impermax-v2": "IMX",
        "jito-liquid-staking": "JITO",
        "lista-lending": "LISTA",
        "moonwell-lending": "WELL"
    }
    
    downloaded = 0
    for protocol in remaining_protocols:
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Searching CMC for protocol: {protocol}")
        
        icon_url = ""
        
        # Стратегия 1: Поиск по токену протокола
        if protocol in protocol_tokens:
            token_symbol = protocol_tokens[protocol]
            print(f"  → Trying protocol token: {token_symbol}")
            icon_url = search_cmc_by_symbol(token_symbol)
            if icon_url:
                print(f"  → Found via protocol token: {token_symbol}")
        
        # Стратегия 2: Поиск по имени протокола
        if not icon_url:
            icon_url = search_cmc_by_name(protocol)
            if icon_url:
                print(f"  → Found via protocol name")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        else:
            print(f"  → No icon found in CMC")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} new protocol icons via CMC")

def main():
    print("🚀 Searching for remaining missing icons via CoinMarketCap API...")
    print(f"Using CMC API Key: {CMC_API_KEY[:8]}...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем оставшиеся иконки через CMC
    download_remaining_chains_via_cmc()
    download_remaining_tokens_via_cmc()
    download_remaining_protocols_via_cmc()
    
    print("\n✅ CMC search complete!")
    print("Check the results and run coverage check again.")

if __name__ == "__main__":
    main()

