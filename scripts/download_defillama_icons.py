#!/usr/bin/env python3
"""
Скрипт для загрузки иконок протоколов и сетей через DeFiLlama API
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
DEFILLAMA_API = "https://api.llama.fi"
ICONS_DIR = Path("frontend/public/icons")
PROTOCOLS_FILE = "frontend/public/data/defillama_protocols.json"
CHAINS_FILE = "frontend/public/data/defillama_chains.json"

# Создаем директории
ICONS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.joinpath("protocols").mkdir(exist_ok=True)
ICONS_DIR.joinpath("chains").mkdir(exist_ok=True)
ICONS_DIR.parent.joinpath("data").mkdir(exist_ok=True)

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

def get_defillama_protocols():
    """Получить список протоколов из DeFiLlama"""
    try:
        response = requests.get(f"{DEFILLAMA_API}/protocols")
        
        if response.status_code == 200:
            protocols = response.json()
            protocol_data = []
            
            for protocol in protocols:
                name = protocol.get("name", "")
                slug = protocol.get("slug", "")
                logo = protocol.get("logo", "")
                
                if name and logo:
                    # Нормализуем имя для файла
                    file_name = name.upper().replace(" ", "").replace("-", "").replace("_", "")
                    file_name = "".join(c for c in file_name if c.isalnum())
                    
                    # Скачиваем иконку
                    icon_path = ICONS_DIR / "protocols" / f"{file_name}.png"
                    if download_image(logo, icon_path):
                        protocol_data.append({
                            "name": name,
                            "slug": slug,
                            "icon": f"/icons/protocols/{file_name}.png",
                            "logo_url": logo
                        })
                
                time.sleep(0.1)  # Rate limiting
            
            # Сохраняем данные
            with open(PROTOCOLS_FILE, 'w') as f:
                json.dump(protocol_data, f, indent=2)
            
            print(f"✓ Downloaded {len(protocol_data)} protocol icons")
            return protocol_data
            
    except Exception as e:
        print(f"✗ Error getting protocols: {e}")
    
    return []

def get_defillama_chains():
    """Получить список сетей из DeFiLlama"""
    try:
        response = requests.get(f"{DEFILLAMA_API}/chains")
        
        if response.status_code == 200:
            chains = response.json()
            chain_data = []
            
            for chain in chains:
                name = chain.get("name", "")
                tokenSymbol = chain.get("tokenSymbol", "")
                logo = chain.get("logo", "")
                
                if name and logo:
                    # Нормализуем имя для файла
                    file_name = name.replace(" ", "").replace("-", "").replace("_", "")
                    
                    # Скачиваем иконку
                    icon_path = ICONS_DIR / "chains" / f"{file_name}.png"
                    if download_image(logo, icon_path):
                        chain_data.append({
                            "name": name,
                            "symbol": tokenSymbol,
                            "icon": f"/icons/chains/{file_name}.png",
                            "logo_url": logo
                        })
                
                time.sleep(0.1)  # Rate limiting
            
            # Сохраняем данные
            with open(CHAINS_FILE, 'w') as f:
                json.dump(chain_data, f, indent=2)
            
            print(f"✓ Downloaded {len(chain_data)} chain icons")
            return chain_data
            
    except Exception as e:
        print(f"✗ Error getting chains: {e}")
    
    return []

def main():
    print("🚀 Starting icon download from DeFiLlama...")
    
    # Скачиваем протоколы
    print("\n🏛️ Downloading protocol icons...")
    protocols = get_defillama_protocols()
    
    # Скачиваем сети
    print("\n🌐 Downloading chain icons...")
    chains = get_defillama_chains()
    
    print(f"\n✅ Complete! Downloaded {len(protocols)} protocols and {len(chains)} chains")
    print(f"📁 Icons saved to: {ICONS_DIR}")
    print(f"📄 Data saved to: {PROTOCOLS_FILE}, {CHAINS_FILE}")

if __name__ == "__main__":
    main()
