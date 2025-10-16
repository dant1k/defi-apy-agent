#!/usr/bin/env python3
"""
Скрипт для получения полного списка элементов без иконок
"""

import os
import requests
import json
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def normalize_name(name: str) -> str:
    """Нормализовать имя для файла"""
    return name.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")

def check_icon_exists(name: str, category: str) -> bool:
    """Проверить, существует ли иконка для элемента"""
    if category == "chains":
        file_name = normalize_name(name)
        local_path = ICONS_DIR / "chains" / f"{file_name}.png"
        backup_path = BACKUP_DIR / "chains" / f"{file_name}.png"
    elif category == "tokens":
        local_path = ICONS_DIR / "tokens" / f"{name}.png"
        backup_path = BACKUP_DIR / "tokens" / f"{name}.png"
    elif category == "protocols":
        import re
        file_name = re.sub(r'[^A-Z0-9]', '', name.upper())
        local_path = ICONS_DIR / "protocols" / f"{file_name}.png"
        backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
    else:
        return False
    
    return local_path.exists() or backup_path.exists()

def get_missing_chains():
    """Получить список сетей без иконок"""
    print("🌐 Getting missing chain icons...")
    
    try:
        response = requests.get("http://localhost:8000/chains")
        if response.status_code == 200:
            chains = response.json().get("items", [])
        else:
            print("❌ Failed to get chains from API")
            return []
    except:
        print("❌ API not available")
        return []
    
    missing_icons = []
    for chain in chains:
        if not check_icon_exists(chain, "chains"):
            missing_icons.append(chain)
    
    return missing_icons

def get_missing_tokens():
    """Получить список токенов без иконок"""
    print("🪙 Getting missing token icons...")
    
    try:
        response = requests.get("http://localhost:8000/tokens?limit=100")
        if response.status_code == 200:
            tokens_data = response.json().get("tokens", [])
            tokens = [token.get("symbol", "") for token in tokens_data if token.get("symbol")]
        else:
            print("❌ Failed to get tokens from API")
            return []
    except:
        print("❌ API not available")
        return []
    
    missing_icons = []
    for token in tokens:
        if not check_icon_exists(token, "tokens"):
            missing_icons.append(token)
    
    return missing_icons

def get_missing_protocols():
    """Получить список протоколов без иконок"""
    print("🏛️ Getting missing protocol icons...")
    
    try:
        response = requests.get("http://localhost:8000/protocols")
        if response.status_code == 200:
            protocols = response.json().get("items", [])
        else:
            print("❌ Failed to get protocols from API")
            return []
    except:
        print("❌ API not available")
        return []
    
    missing_icons = []
    for protocol in protocols:
        if not check_icon_exists(protocol, "protocols"):
            missing_icons.append(protocol)
    
    return missing_icons

def main():
    print("📋 Getting complete list of missing icons...")
    
    missing_chains = get_missing_chains()
    missing_tokens = get_missing_tokens()
    missing_protocols = get_missing_protocols()
    
    print(f"\n📊 Summary:")
    print(f"  Missing chain icons: {len(missing_chains)}")
    print(f"  Missing token icons: {len(missing_tokens)}")
    print(f"  Missing protocol icons: {len(missing_protocols)}")
    print(f"  Total missing: {len(missing_chains) + len(missing_tokens) + len(missing_protocols)}")
    
    print(f"\n🌐 Missing Chain Icons ({len(missing_chains)}):")
    for i, chain in enumerate(missing_chains, 1):
        print(f"  {i:3d}. {chain}")
    
    print(f"\n🪙 Missing Token Icons ({len(missing_tokens)}):")
    for i, token in enumerate(missing_tokens, 1):
        print(f"  {i:3d}. {token}")
    
    print(f"\n🏛️ Missing Protocol Icons ({len(missing_protocols)}):")
    for i, protocol in enumerate(missing_protocols, 1):
        print(f"  {i:3d}. {protocol}")

if __name__ == "__main__":
    main()

