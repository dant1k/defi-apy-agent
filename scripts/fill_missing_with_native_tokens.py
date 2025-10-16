#!/usr/bin/env python3
"""
Скрипт для заполнения недостающих иконок сетей иконками их нативных токенов
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
                coin_id = coin_data.get('id')
                if coin_id:
                    return f"https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png"
    except Exception as e:
        print(f"  → CMC API error for {symbol}: {e}")
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

def get_missing_chains_native_tokens():
    """Маппинг недостающих сетей к их нативным токенам"""
    return {
        "Echelon_initia": "INIT",
        "Fraxtal": "FXTL", 
        "fraxtal": "FXTL",
        "fuse": "FUSE",
        "one": "ONE",
        "zkevm": "ETH"
    }

def fill_missing_chains_with_native_tokens():
    """Заполнить недостающие иконки сетей иконками их нативных токенов"""
    print("🌐 Filling missing chain icons with native token icons...")
    
    # Недостающие сети
    missing_chains = [
        "Echelon_initia", "Fraxtal", "fraxtal", "fuse", "one", "zkevm"
    ]
    
    native_tokens = get_missing_chains_native_tokens()
    
    downloaded = 0
    for chain in missing_chains:
        file_name = normalize_name(chain)
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Looking for native token icon for: {chain}")
        
        icon_url = ""
        
        # Получаем символ нативного токена
        if chain in native_tokens:
            token_symbol = native_tokens[chain]
            print(f"  → Native token: {token_symbol}")
            
            # Стратегия 1: Поиск в CMC
            icon_url = search_cmc_by_symbol(token_symbol)
            if icon_url:
                print(f"  → Found via CMC: {token_symbol}")
            
            # Стратегия 2: Поиск в CoinGecko
            if not icon_url:
                icon_url = search_coingecko_by_symbol(token_symbol)
                if icon_url:
                    print(f"  → Found via CoinGecko: {token_symbol}")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        else:
            print(f"  → No native token icon found")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} native token icons for missing chains")

def fill_missing_tokens():
    """Заполнить недостающие иконки токенов"""
    print("\n🪙 Filling missing token icons...")
    
    missing_tokens = ["DEXE"]
    
    downloaded = 0
    for token in missing_tokens:
        backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Looking for token icon: {token}")
        
        # Стратегия 1: Поиск в CMC
        icon_url = search_cmc_by_symbol(token)
        if icon_url:
            print(f"  → Found via CMC: {token}")
        
        # Стратегия 2: Поиск в CoinGecko
        if not icon_url:
            icon_url = search_coingecko_by_symbol(token)
            if icon_url:
                print(f"  → Found via CoinGecko: {token}")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        else:
            print(f"  → No token icon found")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} missing token icons")

def fill_missing_protocols_with_tokens():
    """Заполнить недостающие иконки протоколов иконками их токенов"""
    print("\n🏛️ Filling missing protocol icons with token icons...")
    
    missing_protocols = [
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
    for protocol in missing_protocols:
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем, если уже есть
        if backup_path.exists():
            continue
        
        print(f"🔍 Looking for protocol token icon: {protocol}")
        
        icon_url = ""
        
        # Получаем символ токена протокола
        if protocol in protocol_tokens:
            token_symbol = protocol_tokens[protocol]
            print(f"  → Protocol token: {token_symbol}")
            
            # Стратегия 1: Поиск в CMC
            icon_url = search_cmc_by_symbol(token_symbol)
            if icon_url:
                print(f"  → Found via CMC: {token_symbol}")
            
            # Стратегия 2: Поиск в CoinGecko
            if not icon_url:
                icon_url = search_coingecko_by_symbol(token_symbol)
                if icon_url:
                    print(f"  → Found via CoinGecko: {token_symbol}")
        
        if icon_url:
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if download_image(icon_url, backup_path):
                downloaded += 1
        else:
            print(f"  → No protocol token icon found")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"✓ Downloaded {downloaded} protocol token icons")

def main():
    print("🚀 Filling missing icons with native token icons...")
    print(f"Using CMC API Key: {CMC_API_KEY[:8]}...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Заполняем недостающие иконки
    fill_missing_chains_with_native_tokens()
    fill_missing_tokens()
    fill_missing_protocols_with_tokens()
    
    print("\n✅ Native token icon filling complete!")
    print("Check the results and run coverage check again.")

if __name__ == "__main__":
    main()

