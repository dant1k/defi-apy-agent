#!/usr/bin/env python3
"""
Скрипт для полного восстановления всех иконок протоколов
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

def get_all_defillama_protocols():
    """Получить все протоколы из DeFiLlama"""
    try:
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Error getting DeFiLlama protocols: {e}")
        return []

def search_coingecko_for_protocol(protocol_name: str):
    """Поиск протокола в CoinGecko"""
    try:
        # Пробуем разные варианты поиска
        search_variants = [
            protocol_name,
            protocol_name.lower(),
            protocol_name.replace("-", " "),
            protocol_name.replace("_", " "),
            protocol_name.replace("v2", "").replace("v3", "").replace("v4", "").strip(),
            protocol_name.replace("-v2", "").replace("-v3", "").replace("-v4", "").strip()
        ]
        
        for variant in search_variants:
            if not variant:
                continue
                
            response = requests.get("https://api.coingecko.com/api/v3/search", params={
                "query": variant
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("coins"):
                    for coin in data["coins"]:
                        coin_name = coin.get("name", "").lower()
                        variant_lower = variant.lower()
                        
                        # Более мягкое сравнение
                        if (variant_lower in coin_name or 
                            coin_name in variant_lower or
                            abs(len(variant_lower) - len(coin_name)) <= 3):
                            return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error searching CoinGecko for {protocol_name}: {e}")
    return ""

def restore_all_missing_protocols():
    """Восстановить все недостающие протоколы"""
    print("🏛️ Restoring ALL missing protocol icons...")
    
    # Получаем все протоколы из DeFiLlama
    defillama_protocols = get_all_defillama_protocols()
    print(f"📊 Found {len(defillama_protocols)} protocols in DeFiLlama")
    
    # Создаем lookup для быстрого поиска
    protocol_lookup = {}
    for protocol in defillama_protocols:
        name = protocol.get("name", "").lower()
        protocol_lookup[name] = protocol
    
    # Список недостающих протоколов (все 75)
    missing_protocols = [
        "3jane-options", "aave-v3", "aerodrome-v1", "alien-base-v2", "alien-base-v3",
        "anzen-v2", "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1",
        "arrakis-v2", "astar-network", "bancor-v3", "compound-v2", "curve-v2",
        "dydx-v4", "euler-v2", "gmx-v2", "kyber-network", "lido-v2",
        "makerdao", "pancakeswap-v3", "sushiswap-v3", "uniswap-v3", "yearn-finance-v2",
        "1inch-v3", "balancer-v2", "convex-finance", "frax-finance", "harvest-finance",
        "iron-bank", "jupiter-aggregator", "kava-lend", "liquity", "moonwell",
        "nexus-mutual", "opyn", "pooltogether-v3", "quickswap-v3", "reflexer",
        "ribbon-finance", "saddle-finance", "synthetix", "tornado-cash", "venus",
        "vesper-finance", "yield-protocol", "zapper", "zerion", "1inch-limit-order-protocol",
        "88mph", "abracadabra-money", "alchemix", "alpha-homora", "anchor-protocol",
        "apricot-finance", "badger-dao", "barnbridge", "benqi", "bent-finance",
        "cream-finance", "defi-pulse-index", "dforce", "dodo", "enzyme-finance",
        "fei-protocol", "flexa", "fuse", "gains-network", "geist-finance",
        "goldfinch", "hundred-finance", "idle-finance", "indexed-finance", "inverse-finance",
        "klima-dao", "lido", "maple-finance", "mstable", "notional-finance"
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
            if icon_url:
                print(f"  → Found in DeFiLlama")
        
        # Стратегия 2: Поиск в CoinGecko
        if not icon_url:
            icon_url = search_coingecko_for_protocol(protocol)
            if icon_url:
                print(f"  → Found in CoinGecko")
        
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
                "lido-v2": ["lido", "lido v2"],
                "makerdao": ["maker", "maker dao"],
                "pancakeswap-v3": ["pancakeswap", "pancakeswap v3"],
                "sushiswap-v3": ["sushiswap", "sushiswap v3"],
                "uniswap-v3": ["uniswap", "uniswap v3"],
                "yearn-finance-v2": ["yearn", "yearn finance", "yearn v2"]
            }
            
            if protocol in alternatives:
                for alt in alternatives[protocol]:
                    icon_url = search_coingecko_for_protocol(alt)
                    if icon_url:
                        print(f"  → Found via alternative: {alt}")
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
        
        # Пауза между запросами
        time.sleep(0.5)
    
    print(f"📊 Restored {restored_count} protocol icons")
    return restored_count

def main():
    print("🚀 Restoring ALL missing protocol icons to achieve 100% coverage...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Восстанавливаем все недостающие протоколы
    restored_count = restore_all_missing_protocols()
    
    print(f"\n📊 Complete Protocol Restoration Summary:")
    print(f"  Total protocol icons restored: {restored_count}")
    
    if restored_count > 0:
        print(f"✅ Successfully restored {restored_count} protocol icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"❌ No protocol icons were restored")

if __name__ == "__main__":
    main()

