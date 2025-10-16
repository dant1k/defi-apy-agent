#!/usr/bin/env python3
"""
Проверяет все иконки для сетей, протоколов и токенов в активных стратегиях.
"""

import os
import requests
import json
from pathlib import Path
from typing import Set, Dict, List

# Настройки
API_URL = "http://localhost:8000"
FRONTEND_ICONS_DIR = Path("frontend/public/icons")
API_ICONS_DIR = Path("api/static/icons")

def get_all_active_items() -> Dict[str, Set[str]]:
    """Получает все активные сети, протоколы и токены."""
    try:
        response = requests.get(f"{API_URL}/strategies?min_tvl=1000000&limit=500")
        response.raise_for_status()
        data = response.json()
        
        chains = set()
        protocols = set()
        tokens = set()
        
        for item in data.get("items", []):
            # Сети
            if item.get("chain"):
                chains.add(item["chain"])
            
            # Протоколы
            if item.get("protocol"):
                protocols.add(item["protocol"])
            
            # Токены из token_pair
            if item.get("token_pair"):
                pair_tokens = item["token_pair"].split("-")
                tokens.update(pair_tokens)
        
        return {
            "chains": chains,
            "protocols": protocols,
            "tokens": tokens
        }
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")
        return {"chains": set(), "protocols": set(), "tokens": set()}

def normalize_name(name: str, category: str) -> str:
    """Нормализует имя для поиска иконки."""
    if category == "chains":
        return name.upper().replace(" ", "").replace("-", "")
    elif category == "protocols":
        return name.upper().replace(" ", "").replace("-", "").replace("_", "")
    else:  # tokens
        return name.upper()

def check_icon_exists(name: str, category: str) -> Dict[str, bool]:
    """Проверяет существование иконки в разных местах."""
    normalized = normalize_name(name, category)
    icon_file = f"{normalized}.png"
    
    frontend_path = FRONTEND_ICONS_DIR / category / icon_file
    api_path = API_ICONS_DIR / category / icon_file
    
    return {
        "name": name,
        "normalized": normalized,
        "frontend_exists": frontend_path.exists(),
        "api_exists": api_path.exists(),
        "frontend_path": str(frontend_path),
        "api_path": str(api_path)
    }

def check_all_icons():
    """Проверяет все иконки."""
    print("🔍 Получаем активные стратегии...")
    items = get_all_active_items()
    
    print(f"📊 Найдено:")
    print(f"  - Сетей: {len(items['chains'])}")
    print(f"  - Протоколов: {len(items['protocols'])}")
    print(f"  - Токенов: {len(items['tokens'])}")
    print()
    
    missing_icons = {
        "chains": [],
        "protocols": [],
        "tokens": []
    }
    
    for category, items_set in items.items():
        print(f"🔍 Проверяем {category}...")
        
        for item in sorted(items_set):
            result = check_icon_exists(item, category)
            
            if not result["frontend_exists"] or not result["api_exists"]:
                missing_icons[category].append(result)
                status = "❌"
                if result["frontend_exists"] and not result["api_exists"]:
                    status = "⚠️ API"
                elif not result["frontend_exists"] and result["api_exists"]:
                    status = "⚠️ Frontend"
            else:
                status = "✅"
            
            print(f"  {status} {item} -> {result['normalized']}.png")
    
    print("\n📋 СВОДКА:")
    for category, missing in missing_icons.items():
        if missing:
            print(f"\n❌ Отсутствующие {category} ({len(missing)}):")
            for item in missing:
                print(f"  - {item['name']} -> {item['normalized']}.png")
                if not item['frontend_exists']:
                    print(f"    Frontend: {item['frontend_path']}")
                if not item['api_exists']:
                    print(f"    API: {item['api_path']}")
        else:
            print(f"✅ Все {category} имеют иконки!")
    
    return missing_icons

if __name__ == "__main__":
    missing = check_all_icons()
    
    total_missing = sum(len(missing[cat]) for cat in missing)
    if total_missing > 0:
        print(f"\n🚨 Всего отсутствует иконок: {total_missing}")
    else:
        print(f"\n🎉 Все иконки на месте!")

