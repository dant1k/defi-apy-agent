#!/usr/bin/env python3
"""
Скрипт для полного восстановления всех недостающих иконок
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

def search_coingecko_icon(query: str, search_type: str = "coin"):
    """Поиск иконки в CoinGecko"""
    try:
        response = requests.get("https://api.coingecko.com/api/v3/search", params={
            "query": query
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("coins"):
                for coin in data["coins"]:
                    coin_name = coin.get("name", "").lower()
                    coin_symbol = coin.get("symbol", "").upper()
                    query_lower = query.lower()
                    
                    # Различные стратегии поиска
                    if (query_lower in coin_name or 
                        coin_name in query_lower or
                        coin_symbol == query.upper() or
                        query_lower.replace(" ", "") in coin_name.replace(" ", "") or
                        coin_name.replace(" ", "") in query_lower.replace(" ", "")):
                        return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error searching CoinGecko for {query}: {e}")
    return ""

def search_defillama_protocols():
    """Получить все протоколы из DeFiLlama"""
    try:
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting DeFiLlama protocols: {e}")
        return []

def search_defillama_chains():
    """Получить все сети из DeFiLlama"""
    try:
        response = requests.get("https://api.llama.fi/chains")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting DeFiLlama chains: {e}")
        return []

def restore_missing_chain_icons():
    """Восстановить все недостающие иконки сетей"""
    print("🌐 Restoring ALL missing chain icons...")
    
    missing_chains = [
        "Bifrost Network", "Bitcoincash", "Boba", "Litecoin", "Ripple", 
        "Rollux", "zkSync Era"
    ]
    
    # Получаем все сети из DeFiLlama для поиска
    defillama_chains = search_defillama_chains()
    chain_lookup = {chain.get("name", "").lower(): chain for chain in defillama_chains}
    
    restored_count = 0
    
    for chain in missing_chains:
        print(f"🔍 Searching for {chain}...")
        icon_url = ""
        
        # Стратегия 1: Поиск в DeFiLlama
        chain_lower = chain.lower()
        if chain_lower in chain_lookup:
            defillama_chain = chain_lookup[chain_lower]
            if defillama_chain.get("gecko_id"):
                # Получаем иконку через CoinGecko
                try:
                    response = requests.get(f"https://api.coingecko.com/api/v3/coins/{defillama_chain['gecko_id']}")
                    if response.status_code == 200:
                        data = response.json()
                        icon_url = data.get("image", {}).get("large", "")
                except:
                    pass
        
        # Стратегия 2: Поиск в CoinGecko
        if not icon_url:
            icon_url = search_coingecko_icon(chain)
        
        # Стратегия 3: Альтернативные названия
        if not icon_url:
            alternatives = {
                "Bifrost Network": ["bifrost", "bifrost-kusama"],
                "Bitcoincash": ["bitcoin-cash", "bch"],
                "Boba": ["boba-network", "boba"],
                "Litecoin": ["litecoin", "ltc"],
                "Ripple": ["ripple", "xrp"],
                "Rollux": ["rollux", "syscoin"],
                "zkSync Era": ["zksync", "zksync-era", "zksync era"]
            }
            
            if chain in alternatives:
                for alt in alternatives[chain]:
                    icon_url = search_coingecko_icon(alt)
                    if icon_url:
                        break
        
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
    """Восстановить все недостающие иконки токенов"""
    print("🪙 Restoring ALL missing token icons...")
    
    missing_tokens = ["IOTA"]
    
    restored_count = 0
    
    for token in missing_tokens:
        print(f"🔍 Searching for {token}...")
        
        # Стратегия 1: Прямой поиск
        icon_url = search_coingecko_icon(token)
        
        # Стратегия 2: Альтернативные названия
        if not icon_url:
            alternatives = {
                "IOTA": ["iota", "miota", "iota-tangle"]
            }
            
            if token in alternatives:
                for alt in alternatives[token]:
                    icon_url = search_coingecko_icon(alt)
                    if icon_url:
                        break
        
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
    """Восстановить все недостающие иконки протоколов"""
    print("🏛️ Restoring ALL missing protocol icons...")
    
    # Получаем все протоколы из DeFiLlama
    defillama_protocols = search_defillama_protocols()
    protocol_lookup = {protocol.get("name", "").lower(): protocol for protocol in defillama_protocols}
    
    # Список недостающих протоколов (первые 20 для тестирования)
    missing_protocols = [
        "3jane-options", "aave-v3", "aerodrome-v1", "alien-base-v2", "alien-base-v3",
        "anzen-v2", "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1",
        "arrakis-v2", "astar-network", "bancor-v3", "compound-v2", "curve-v2",
        "dydx-v4", "euler-v2", "gmx-v2", "kyber-network", "lido-v2"
    ]
    
    restored_count = 0
    
    for protocol in missing_protocols:
        print(f"🔍 Searching for {protocol}...")
        icon_url = ""
        
        # Стратегия 1: Поиск в DeFiLlama
        protocol_lower = protocol.lower()
        if protocol_lower in protocol_lookup:
            defillama_protocol = protocol_lookup[protocol_lower]
            icon_url = defillama_protocol.get("logo", "")
        
        # Стратегия 2: Поиск в CoinGecko
        if not icon_url:
            icon_url = search_coingecko_icon(protocol)
        
        # Стратегия 3: Альтернативные названия
        if not icon_url:
            alternatives = {
                "3jane-options": ["3jane", "3jane options"],
                "aave-v3": ["aave", "aave v3"],
                "aerodrome-v1": ["aerodrome", "aerodrome v1"],
                "alien-base-v2": ["alien base", "alien base v2"],
                "alien-base-v3": ["alien base v3"],
                "anzen-v2": ["anzen", "anzen v2"],
                "apeswap-lending": ["apeswap", "apeswap lending"],
                "aptin-finance-v2": ["aptin", "aptin finance"],
                "arcadia-v2": ["arcadia", "arcadia v2"],
                "arrakis-v1": ["arrakis", "arrakis v1"],
                "arrakis-v2": ["arrakis v2"],
                "astar-network": ["astar", "astar network"],
                "bancor-v3": ["bancor", "bancor v3"],
                "compound-v2": ["compound", "compound v2"],
                "curve-v2": ["curve", "curve v2"],
                "dydx-v4": ["dydx", "dydx v4"],
                "euler-v2": ["euler", "euler v2"],
                "gmx-v2": ["gmx", "gmx v2"],
                "kyber-network": ["kyber", "kyber network"],
                "lido-v2": ["lido", "lido v2"]
            }
            
            if protocol in alternatives:
                for alt in alternatives[protocol]:
                    icon_url = search_coingecko_icon(alt)
                    if icon_url:
                        break
        
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
    print("🔄 Restoring ALL missing icons to achieve 100% coverage...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_restored = 0
    
    # Восстанавливаем все недостающие иконки
    total_restored += restore_missing_chain_icons()
    total_restored += restore_missing_token_icons()
    total_restored += restore_missing_protocol_icons()
    
    print(f"\n📊 Complete Restoration Summary:")
    print(f"  Total icons restored: {total_restored}")
    
    if total_restored > 0:
        print(f"✅ Successfully restored {total_restored} missing icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"❌ No icons were restored")

if __name__ == "__main__":
    main()

