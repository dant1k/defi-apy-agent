#!/usr/bin/env python3
"""
Скрипт для проверки покрытия иконками всех элементов в выпадающих меню
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

def check_chains():
    """Проверить покрытие иконками для сетей"""
    print("🌐 Checking chain icon coverage...")
    
    try:
        response = requests.get("http://localhost:8000/chains")
        if response.status_code == 200:
            chains = response.json().get("items", [])
        else:
            print("❌ Failed to get chains from API")
            return
    except:
        print("❌ API not available")
        return
    
    missing_icons = []
    for chain in chains:
        if not check_icon_exists(chain, "chains"):
            missing_icons.append(chain)
    
    print(f"📊 Chains: {len(chains)} total, {len(chains) - len(missing_icons)} with icons, {len(missing_icons)} missing")
    
    if missing_icons:
        print("❌ Missing chain icons:")
        for chain in missing_icons[:10]:  # Показываем первые 10
            print(f"  - {chain}")
        if len(missing_icons) > 10:
            print(f"  ... and {len(missing_icons) - 10} more")
    
    return missing_icons

def check_tokens():
    """Проверить покрытие иконками для токенов"""
    print("\n🪙 Checking token icon coverage...")
    
    try:
        response = requests.get("http://localhost:8000/tokens?limit=100")
        if response.status_code == 200:
            tokens_data = response.json().get("tokens", [])
            tokens = [token.get("symbol", "") for token in tokens_data if token.get("symbol")]
        else:
            print("❌ Failed to get tokens from API")
            return
    except:
        print("❌ API not available")
        return
    
    missing_icons = []
    for token in tokens:
        if not check_icon_exists(token, "tokens"):
            missing_icons.append(token)
    
    print(f"📊 Tokens: {len(tokens)} total, {len(tokens) - len(missing_icons)} with icons, {len(missing_icons)} missing")
    
    if missing_icons:
        print("❌ Missing token icons:")
        for token in missing_icons[:10]:  # Показываем первые 10
            print(f"  - {token}")
        if len(missing_icons) > 10:
            print(f"  ... and {len(missing_icons) - 10} more")
    
    return missing_icons

def check_protocols():
    """Проверить покрытие иконками для протоколов"""
    print("\n🏛️ Checking protocol icon coverage...")
    
    try:
        response = requests.get("http://localhost:8000/protocols")
        if response.status_code == 200:
            protocols = response.json().get("items", [])
        else:
            print("❌ Failed to get protocols from API")
            return
    except:
        print("❌ API not available")
        return
    
    missing_icons = []
    for protocol in protocols:
        if not check_icon_exists(protocol, "protocols"):
            missing_icons.append(protocol)
    
    print(f"📊 Protocols: {len(protocols)} total, {len(protocols) - len(missing_icons)} with icons, {len(missing_icons)} missing")
    
    if missing_icons:
        print("❌ Missing protocol icons:")
        for protocol in missing_icons[:10]:  # Показываем первые 10
            print(f"  - {protocol}")
        if len(missing_icons) > 10:
            print(f"  ... and {len(missing_icons) - 10} more")
    
    return missing_icons

def main():
    print("🔍 Checking icon coverage for all dropdown menu items...")
    
    missing_chains = check_chains()
    missing_tokens = check_tokens()
    missing_protocols = check_protocols()
    
    total_missing = len(missing_chains) + len(missing_tokens) + len(missing_protocols)
    
    print(f"\n📊 Summary:")
    print(f"  Missing chain icons: {len(missing_chains)}")
    print(f"  Missing token icons: {len(missing_tokens)}")
    print(f"  Missing protocol icons: {len(missing_protocols)}")
    print(f"  Total missing: {total_missing}")
    
    if total_missing == 0:
        print("✅ All dropdown menu items have icons!")
    else:
        print("❌ Some dropdown menu items are missing icons.")

if __name__ == "__main__":
    main()
