#!/usr/bin/env python3
"""
Скрипт для создания недостающих иконок протоколов из базовых версий
"""

import os
import shutil
from pathlib import Path

# Настройки
BACKUP_DIR = Path("api/static/icons")

def create_icon_mappings():
    """Создать маппинги для создания недостающих иконок"""
    mappings = {
        # Версии протоколов - копируем из базовых версий
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
        "lido-v2": "lido",
        "makerdao": "maker",
        "kyber-network": "kyber",
        "gmx-v2": "gmx",
        "dydx-v4": "dydx",
        "euler-v2": "euler",
        "bancor-v3": "bancor",
        "arrakis-v1": "arrakis",
        "arrakis-v2": "arrakis",
        "arcadia-v2": "arcadia",
        "aptin-finance-v2": "aptin-finance",
        "apeswap-lending": "apeswap",
        "anzen-v2": "anzen",
        "alien-base-v3": "alien-base-v2",
        "alien-base-v2": "base",
        "3jane-options": "3jane",
        
        # Похожие протоколы
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
        "notional-finance": "notional",
        "avalon-finance": "avalon"
    }
    
    return mappings

def copy_icon_if_exists(source_name: str, target_name: str):
    """Копировать иконку если источник существует"""
    try:
        import re
        source_file = re.sub(r'[^A-Z0-9]', '', source_name.upper())
        target_file = re.sub(r'[^A-Z0-9]', '', target_name.upper())
        
        source_path = BACKUP_DIR / "protocols" / f"{source_file}.png"
        target_path = BACKUP_DIR / "protocols" / f"{target_file}.png"
        
        if source_path.exists() and not target_path.exists():
            shutil.copy2(source_path, target_path)
            print(f"✓ Created: {target_name} from {source_name}")
            return True
        elif not source_path.exists():
            print(f"❌ Source not found: {source_name}")
        elif target_path.exists():
            print(f"⚠️  Target already exists: {target_name}")
        return False
    except Exception as e:
        print(f"✗ Failed to copy {source_name} → {target_name}: {e}")
        return False

def create_missing_icons():
    """Создать недостающие иконки"""
    print("🏛️ Creating missing protocol icons from existing ones...")
    
    mappings = create_icon_mappings()
    created_count = 0
    
    for target, source in mappings.items():
        if copy_icon_if_exists(source, target):
            created_count += 1
    
    print(f"📊 Created {created_count} protocol icons")
    return created_count

def create_fallback_icons():
    """Создать fallback иконки для оставшихся протоколов"""
    print("🔄 Creating fallback icons for remaining protocols...")
    
    # Список оставшихся протоколов без иконок
    remaining_protocols = [
        "3jane-options", "alien-base-v2", "alien-base-v3", "anzen-v2", 
        "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1",
        "avalon-finance", "balancer-v2", "bancor-v3", "compound-v2",
        "convex-finance", "curve-v2", "dydx-v4", "frax-finance",
        "harvest-finance", "iron-bank", "jupiter-aggregator", "kava-lend",
        "kyber-network", "liquity", "makerdao", "moonwell", "nexus-mutual",
        "opyn", "pooltogether-v3", "reflexer", "ribbon-finance", "saddle-finance",
        "synthetix", "tornado-cash", "venus", "vesper-finance", "yield-protocol",
        "zapper", "zerion", "1inch-limit-order-protocol", "88mph", "abracadabra-money",
        "alchemix", "alpha-homora", "anchor-protocol", "apricot-finance", "badger-dao",
        "barnbridge", "benqi", "bent-finance", "cream-finance", "defi-pulse-index",
        "dforce", "dodo", "enzyme-finance", "fei-protocol", "flexa", "fuse",
        "gains-network", "geist-finance", "goldfinch", "hundred-finance", "idle-finance",
        "indexed-finance", "inverse-finance", "klima-dao", "lido", "maple-finance",
        "mstable", "notional-finance"
    ]
    
    # Базовые протоколы для копирования
    base_protocols = ["ethereum", "defi", "default"]
    
    created_count = 0
    
    for protocol in remaining_protocols:
        # Пробуем найти подходящий базовый протокол
        for base in base_protocols:
            if copy_icon_if_exists(base, protocol):
                created_count += 1
                break
    
    print(f"📊 Created {created_count} fallback protocol icons")
    return created_count

def main():
    print("🚀 Creating all missing protocol icons...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_created = 0
    
    # Стратегия 1: Создание из существующих иконок
    total_created += create_missing_icons()
    
    # Стратегия 2: Создание fallback иконок
    total_created += create_fallback_icons()
    
    print(f"\n📊 Icon Creation Summary:")
    print(f"  Total protocol icons created: {total_created}")
    
    if total_created > 0:
        print(f"✅ Successfully created {total_created} protocol icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"❌ No protocol icons were created")

if __name__ == "__main__":
    main()

