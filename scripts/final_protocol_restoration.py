#!/usr/bin/env python3
"""
Финальный скрипт для восстановления всех оставшихся протоколов
"""

import os
import requests
import json
import time
from pathlib import Path
import shutil

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

def copy_existing_icon(source_name: str, target_name: str):
    """Копировать существующую иконку для похожего протокола"""
    try:
        import re
        source_file = re.sub(r'[^A-Z0-9]', '', source_name.upper())
        target_file = re.sub(r'[^A-Z0-9]', '', target_name.upper())
        
        source_path = BACKUP_DIR / "protocols" / f"{source_file}.png"
        target_path = BACKUP_DIR / "protocols" / f"{target_file}.png"
        
        if source_path.exists() and not target_path.exists():
            shutil.copy2(source_path, target_path)
            print(f"✓ Copied: {source_name} → {target_name}")
            return True
        return False
    except Exception as e:
        print(f"✗ Failed to copy {source_name} → {target_name}: {e}")
        return False

def create_icon_mappings():
    """Создать маппинги для копирования иконок похожих протоколов"""
    mappings = {
        # Версии протоколов
        "aave-v3": "aave",
        "compound-v2": "compound",
        "curve-v2": "curve",
        "uniswap-v3": "uniswap",
        "sushiswap-v3": "sushiswap",
        "pancakeswap-v3": "pancakeswap",
        "yearn-finance-v2": "yearn-finance",
        "balancer-v2": "balancer",
        "1inch-v3": "1inch",
        "quickswap-v3": "quickswap",
        "pooltogether-v3": "pooltogether",
        
        # Похожие протоколы
        "alien-base-v2": "base",
        "alien-base-v3": "base",
        "anzen-v2": "anzen",
        "apeswap-lending": "apeswap",
        "aptin-finance-v2": "aptin-finance",
        "arcadia-v2": "arcadia",
        "arrakis-v1": "arrakis",
        "arrakis-v2": "arrakis",
        "astar-network": "astar",
        "bancor-v3": "bancor",
        "dydx-v4": "dydx",
        "euler-v2": "euler",
        "gmx-v2": "gmx",
        "kyber-network": "kyber",
        "lido-v2": "lido",
        "makerdao": "maker",
        
        # Другие протоколы
        "3jane-options": "3jane",
        "convex-finance": "convex",
        "frax-finance": "frax",
        "harvest-finance": "harvest",
        "iron-bank": "iron",
        "jupiter-aggregator": "jupiter",
        "kava-lend": "kava",
        "liquity": "liquity",
        "moonwell": "moonwell",
        "nexus-mutual": "nexus",
        "opyn": "opyn",
        "reflexer": "reflexer",
        "ribbon-finance": "ribbon",
        "saddle-finance": "saddle",
        "synthetix": "synthetix",
        "tornado-cash": "tornado",
        "venus": "venus",
        "vesper-finance": "vesper",
        "yield-protocol": "yield",
        "zapper": "zapper",
        "zerion": "zerion",
        "1inch-limit-order-protocol": "1inch",
        "88mph": "88mph",
        "abracadabra-money": "abracadabra",
        "alchemix": "alchemix",
        "alpha-homora": "alpha",
        "anchor-protocol": "anchor",
        "apricot-finance": "apricot",
        "badger-dao": "badger",
        "barnbridge": "barnbridge",
        "benqi": "benqi",
        "bent-finance": "bent",
        "cream-finance": "cream",
        "defi-pulse-index": "defi-pulse",
        "dforce": "dforce",
        "dodo": "dodo",
        "enzyme-finance": "enzyme",
        "fei-protocol": "fei",
        "flexa": "flexa",
        "fuse": "fuse",
        "gains-network": "gains",
        "geist-finance": "geist",
        "goldfinch": "goldfinch",
        "hundred-finance": "hundred",
        "idle-finance": "idle",
        "indexed-finance": "indexed",
        "inverse-finance": "inverse",
        "klima-dao": "klima",
        "lido": "lido",
        "maple-finance": "maple",
        "mstable": "mstable",
        "notional-finance": "notional"
    }
    
    return mappings

def restore_remaining_protocols():
    """Восстановить оставшиеся протоколы через копирование"""
    print("🏛️ Restoring remaining protocols via icon mapping...")
    
    mappings = create_icon_mappings()
    restored_count = 0
    
    for target, source in mappings.items():
        if copy_existing_icon(source, target):
            restored_count += 1
    
    print(f"📊 Restored {restored_count} protocols via mapping")
    return restored_count

def search_missing_in_defillama():
    """Поиск недостающих протоколов в DeFiLlama"""
    print("🔍 Searching for missing protocols in DeFiLlama...")
    
    try:
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            protocols = response.json()
            
            # Создаем lookup
            protocol_lookup = {}
            for protocol in protocols:
                name = protocol.get("name", "").lower()
                protocol_lookup[name] = protocol
            
            # Список недостающих протоколов
            missing_protocols = [
                "3jane-options", "alien-base-v2", "alien-base-v3", "anzen-v2", 
                "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1",
                "astroport", "avalon-finance", "bancor-v3", "compound-v2", 
                "convex-finance", "curve-v2", "dydx-v4", "frax-finance",
                "harvest-finance", "iron-bank", "jupiter-aggregator", "kava-lend"
            ]
            
            restored_count = 0
            
            for protocol in missing_protocols:
                protocol_lower = protocol.lower()
                if protocol_lower in protocol_lookup:
                    defillama_protocol = protocol_lookup[protocol_lower]
                    logo_url = defillama_protocol.get("logo", "")
                    
                    if logo_url:
                        import re
                        file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
                        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
                        
                        if download_image(logo_url, backup_path):
                            restored_count += 1
                            print(f"✅ Restored {protocol} from DeFiLlama")
                        else:
                            print(f"❌ Failed to download {protocol}")
                    else:
                        print(f"❌ No logo for {protocol}")
                else:
                    print(f"❌ {protocol} not found in DeFiLlama")
            
            print(f"📊 Restored {restored_count} protocols from DeFiLlama")
            return restored_count
            
    except Exception as e:
        print(f"Error searching DeFiLlama: {e}")
        return 0

def main():
    print("🚀 Final restoration of all remaining protocol icons...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_restored = 0
    
    # Стратегия 1: Поиск в DeFiLlama
    total_restored += search_missing_in_defillama()
    
    # Стратегия 2: Копирование похожих иконок
    total_restored += restore_remaining_protocols()
    
    print(f"\n📊 Final Protocol Restoration Summary:")
    print(f"  Total protocol icons restored: {total_restored}")
    
    if total_restored > 0:
        print(f"✅ Successfully restored {total_restored} protocol icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"❌ No protocol icons were restored")

if __name__ == "__main__":
    main()

