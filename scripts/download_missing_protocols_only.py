#!/usr/bin/env python3
"""
Скрипт для скачивания только недостающих иконок протоколов из DeFiLlama
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

def get_missing_protocols():
    """Получить список недостающих протоколов"""
    print("🔍 Getting list of missing protocols...")
    
    # Список недостающих протоколов из последней проверки
    missing_protocols = [
        "beets-dex-v3", "blend-pools", "blend-pools-v2", "bmx-classic-perps", 
        "camelot-v3", "carrot-liquidity", "cetus-amm", "demex-perp", 
        "flowx-v2", "flowx-v3", "gmx-v2", "hyperliquid-perps", 
        "jupiter-aggregator", "kava-lend", "kyber-network", "lido-v2",
        "makerdao", "moonwell", "nexus-mutual", "opyn", "pooltogether-v3",
        "reflexer", "ribbon-finance", "saddle-finance", "synthetix",
        "tornado-cash", "venus", "vesper-finance", "yield-protocol",
        "zapper", "zerion", "1inch-limit-order-protocol", "88mph",
        "abracadabra-money", "alchemix", "alpha-homora", "anchor-protocol",
        "apricot-finance", "badger-dao", "barnbridge", "benqi",
        "bent-finance", "cream-finance", "defi-pulse-index", "dforce",
        "dodo", "enzyme-finance", "fei-protocol", "flexa", "fuse",
        "gains-network", "geist-finance", "goldfinch", "hundred-finance",
        "idle-finance", "indexed-finance", "inverse-finance", "klima-dao",
        "lido", "maple-finance", "mstable", "notional-finance"
    ]
    
    print(f"📊 Found {len(missing_protocols)} missing protocols")
    return missing_protocols

def get_all_defillama_protocols():
    """Получить ВСЕ протоколы из DeFiLlama"""
    try:
        print("🔍 Fetching ALL protocols from DeFiLlama...")
        response = requests.get("https://api.llama.fi/protocols")
        if response.status_code == 200:
            protocols = response.json()
            print(f"📊 Found {len(protocols)} protocols in DeFiLlama")
            return protocols
        return []
    except Exception as e:
        print(f"Error getting DeFiLlama protocols: {e}")
        return []

def find_missing_in_defillama():
    """Найти недостающие протоколы в DeFiLlama"""
    print("🔍 Finding missing protocols in DeFiLlama...")
    
    missing_protocols = get_missing_protocols()
    all_protocols = get_all_defillama_protocols()
    
    if not all_protocols:
        print("❌ No protocols found in DeFiLlama")
        return []
    
    # Создаем lookup для быстрого поиска
    protocol_lookup = {}
    for protocol in all_protocols:
        name = protocol.get("name", "").lower()
        protocol_lookup[name] = protocol
    
    found_protocols = []
    
    for missing in missing_protocols:
        missing_lower = missing.lower()
        
        # Пробуем найти точное совпадение
        if missing_lower in protocol_lookup:
            found_protocols.append(protocol_lookup[missing_lower])
            print(f"✅ Found exact match: {missing}")
            continue
        
        # Пробуем найти похожие названия
        for defillama_name, protocol in protocol_lookup.items():
            if (missing_lower in defillama_name or 
                defillama_name in missing_lower or
                missing_lower.replace("-", " ") in defillama_name or
                missing_lower.replace("_", " ") in defillama_name):
                found_protocols.append(protocol)
                print(f"✅ Found similar match: {missing} → {defillama_name}")
                break
    
    print(f"📊 Found {len(found_protocols)} matching protocols in DeFiLlama")
    return found_protocols

def download_missing_protocol_icons():
    """Скачать иконки недостающих протоколов"""
    print("🏛️ Downloading missing protocol icons from DeFiLlama...")
    
    found_protocols = find_missing_in_defillama()
    if not found_protocols:
        print("❌ No matching protocols found")
        return 0
    
    downloaded_count = 0
    
    for i, protocol in enumerate(found_protocols, 1):
        protocol_name = protocol.get("name", "")
        logo_url = protocol.get("logo", "")
        
        if not protocol_name or not logo_url:
            continue
        
        print(f"[{i}/{len(found_protocols)}] Processing: {protocol_name}")
        
        # Нормализуем имя для файла
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol_name.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем если уже существует
        if backup_path.exists():
            print(f"  ⚠️  Already exists: {file_name}.png")
            continue
        
        if download_image(logo_url, backup_path):
            downloaded_count += 1
        
        # Пауза между запросами
        time.sleep(0.1)
    
    print(f"📊 Downloaded {downloaded_count} missing protocol icons")
    return downloaded_count

def main():
    print("🚀 Downloading only missing protocol icons from DeFiLlama...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем только недостающие иконки протоколов
    downloaded_count = download_missing_protocol_icons()
    
    print(f"\n📊 Missing Protocols Download Summary:")
    print(f"  Total missing protocol icons downloaded: {downloaded_count}")
    
    if downloaded_count > 0:
        print(f"✅ Successfully downloaded {downloaded_count} missing protocol icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"ℹ️  No missing protocol icons were downloaded")

if __name__ == "__main__":
    main()

