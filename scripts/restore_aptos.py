#!/usr/bin/env python3
"""
Скрипт для восстановления правильного Aptos
"""

import os
import requests
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

def restore_aptos():
    """Восстановить правильный Aptos"""
    print("🔄 Restoring correct Aptos...")
    
    try:
        # Получаем данные о сетях из DeFiLlama
        response = requests.get("https://api.llama.fi/chains")
        if response.status_code == 200:
            chains = response.json()
            
            # Ищем Aptos
            for chain in chains:
                if chain.get("name", "").lower() == "aptos":
                    logo_url = chain.get("logo", "")
                    if logo_url:
                        backup_path = BACKUP_DIR / "chains" / "Aptos.png"
                        if download_image(logo_url, backup_path):
                            print(f"✅ Restored Aptos from DeFiLlama")
                            return True
                        else:
                            print(f"❌ Failed to download Aptos")
                            return False
            
            print(f"❌ Aptos not found in DeFiLlama chains")
            return False
        else:
            print(f"❌ Failed to fetch chains from DeFiLlama")
            return False
            
    except Exception as e:
        print(f"❌ Error restoring Aptos: {e}")
        return False

def main():
    print("🚀 Restoring correct Aptos...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    if restore_aptos():
        print(f"✅ Successfully restored Aptos!")
    else:
        print(f"❌ Failed to restore Aptos")

if __name__ == "__main__":
    main()

