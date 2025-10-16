#!/usr/bin/env python3
"""
Скрипт для восстановления недостающих иконок после удаления дубликатов
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

def get_chain_icon_from_coingecko(chain_name: str):
    """Получить иконку сети из CoinGecko"""
    try:
        # Пробуем разные варианты поиска
        search_terms = [chain_name, chain_name.lower(), chain_name.replace(" ", "-")]
        
        for term in search_terms:
            response = requests.get("https://api.coingecko.com/api/v3/search", params={
                "query": term
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("coins"):
                    for coin in data["coins"]:
                        coin_name = coin.get("name", "").lower()
                        if chain_name.lower() in coin_name or coin_name in chain_name.lower():
                            return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error getting {chain_name} icon from CoinGecko: {e}")
    return ""

def get_token_icon_from_coingecko(token_symbol: str):
    """Получить иконку токена из CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": token_symbol
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                for coin in data["coins"]:
                    if coin.get("symbol", "").upper() == token_symbol.upper():
                        return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error getting {token_symbol} icon from CoinGecko: {e}")
    return ""

def get_protocol_icon_from_defillama(protocol_name: str):
    """Получить иконку протокола из DeFiLlama"""
    try:
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            protocols = response.json()
            for protocol in protocols:
                if protocol.get("name", "").lower() == protocol_name.lower():
                    return protocol.get("logo", "")
        
        return ""
    except Exception as e:
        print(f"Error getting {protocol_name} icon from DeFiLlama: {e}")
    return ""

def restore_missing_chain_icons():
    """Восстановить недостающие иконки сетей"""
    print("🌐 Restoring missing chain icons...")
    
    missing_chains = [
        "Algorand", "Arbitrum", "Bifrost Network", "Bitcoincash", "Boba", 
        "ICP", "Icp", "Litecoin", "Ripple", "Rollux", "SXnetwork", 
        "Stellar", "TON", "WorldChain", "Zksync Era", "zkSync Era"
    ]
    
    restored_count = 0
    
    for chain in missing_chains:
        print(f"🔍 Searching for {chain}...")
        
        # Пробуем получить иконку из CoinGecko
        icon_url = get_chain_icon_from_coingecko(chain)
        
        if icon_url:
            # Нормализуем имя для файла
            import re
            file_name = re.sub(r'[^A-Z0-9]', '', chain.upper())
            backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
            
            if download_image(icon_url, backup_path):
                restored_count += 1
                print(f"✅ Restored {chain}")
            else:
                print(f"❌ Failed to download {chain}")
        else:
            print(f"❌ Icon not found for {chain}")
    
    print(f"📊 Restored {restored_count} chain icons")
    return restored_count

def restore_missing_token_icons():
    """Восстановить недостающие иконки токенов"""
    print("🪙 Restoring missing token icons...")
    
    missing_tokens = ["IOTA"]
    
    restored_count = 0
    
    for token in missing_tokens:
        print(f"🔍 Searching for {token}...")
        
        # Пробуем получить иконку из CoinGecko
        icon_url = get_token_icon_from_coingecko(token)
        
        if icon_url:
            backup_path = BACKUP_DIR / "tokens" / f"{token}.png"
            
            if download_image(icon_url, backup_path):
                restored_count += 1
                print(f"✅ Restored {token}")
            else:
                print(f"❌ Failed to download {token}")
        else:
            print(f"❌ Icon not found for {token}")
    
    print(f"📊 Restored {restored_count} token icons")
    return restored_count

def restore_missing_protocol_icons():
    """Восстановить недостающие иконки протоколов"""
    print("🏛️ Restoring missing protocol icons...")
    
    missing_protocols = [
        "3jane-options", "aave-v3", "aerodrome-v1", "alien-base-v2", "alien-base-v3",
        "anzen-v2", "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1"
    ]
    
    restored_count = 0
    
    for protocol in missing_protocols:
        print(f"🔍 Searching for {protocol}...")
        
        # Пробуем получить иконку из DeFiLlama
        icon_url = get_protocol_icon_from_defillama(protocol)
        
        if icon_url:
            # Нормализуем имя для файла
            import re
            file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
            backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
            
            if download_image(icon_url, backup_path):
                restored_count += 1
                print(f"✅ Restored {protocol}")
            else:
                print(f"❌ Failed to download {protocol}")
        else:
            print(f"❌ Icon not found for {protocol}")
    
    print(f"📊 Restored {restored_count} protocol icons")
    return restored_count

def main():
    print("🔄 Restoring missing icons after duplicate removal...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_restored = 0
    
    # Восстанавливаем недостающие иконки
    total_restored += restore_missing_chain_icons()
    total_restored += restore_missing_token_icons()
    total_restored += restore_missing_protocol_icons()
    
    print(f"\n📊 Restoration Summary:")
    print(f"  Total icons restored: {total_restored}")
    
    if total_restored > 0:
        print(f"✅ Successfully restored {total_restored} missing icons!")
    else:
        print(f"❌ No icons were restored")

if __name__ == "__main__":
    main()

