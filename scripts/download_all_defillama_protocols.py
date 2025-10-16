#!/usr/bin/env python3
"""
Скрипт для скачивания ВСЕХ иконок протоколов из DeFiLlama
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

def download_all_protocol_icons():
    """Скачать иконки ВСЕХ протоколов из DeFiLlama"""
    print("🏛️ Downloading ALL protocol icons from DeFiLlama...")
    
    protocols = get_all_defillama_protocols()
    if not protocols:
        print("❌ No protocols found")
        return 0
    
    downloaded_count = 0
    skipped_count = 0
    
    for i, protocol in enumerate(protocols, 1):
        protocol_name = protocol.get("name", "")
        logo_url = protocol.get("logo", "")
        
        if not protocol_name or not logo_url:
            skipped_count += 1
            continue
        
        print(f"[{i}/{len(protocols)}] Processing: {protocol_name}")
        
        # Нормализуем имя для файла
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', protocol_name.upper())
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
        
        # Пропускаем если уже существует
        if backup_path.exists():
            print(f"  ⚠️  Already exists: {file_name}.png")
            skipped_count += 1
            continue
        
        if download_image(logo_url, backup_path):
            downloaded_count += 1
        else:
            skipped_count += 1
        
        # Пауза между запросами
        time.sleep(0.1)
    
    print(f"📊 Downloaded {downloaded_count} new protocol icons")
    print(f"📊 Skipped {skipped_count} protocols (already exist or no logo)")
    return downloaded_count

def main():
    print("🚀 Downloading ALL protocol icons from DeFiLlama...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Скачиваем все иконки протоколов
    downloaded_count = download_all_protocol_icons()
    
    print(f"\n📊 Complete Download Summary:")
    print(f"  Total new protocol icons downloaded: {downloaded_count}")
    
    if downloaded_count > 0:
        print(f"✅ Successfully downloaded {downloaded_count} protocol icons!")
        print(f"🎯 Now checking final coverage...")
    else:
        print(f"ℹ️  No new protocol icons were downloaded (all already exist)")

if __name__ == "__main__":
    main()

