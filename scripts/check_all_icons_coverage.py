#!/usr/bin/env python3
"""
Проверяет покрытие иконок для всех активных сетей, протоколов и токенов.
"""

import os
import requests
from pathlib import Path

# Настройки
FRONTEND_ICONS_DIR = Path("frontend/public/icons")
API_ICONS_DIR = Path("api/static/icons")

def normalize_name(name: str, category: str) -> str:
    """Нормализует имя для поиска иконки."""
    if category == "chains":
        return name.upper().replace(" ", "").replace("-", "").replace("_", "").replace(".", "")
    elif category == "protocols":
        return name.upper().replace(" ", "").replace("-", "").replace("_", "")
    else:  # tokens
        return name.upper()

def check_icon_exists(name: str, category: str) -> dict:
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

def test_api_icon(category: str, normalized: str) -> bool:
    """Тестирует доступность иконки через API."""
    try:
        response = requests.get(f"http://localhost:8000/icons/{category}/{normalized}.png", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_coverage():
    """Проверяет покрытие иконок для всех активных элементов."""
    
    # Читаем списки из файлов
    with open("/tmp/chains.txt", "r") as f:
        chains = [line.strip() for line in f if line.strip()]
    
    with open("/tmp/protocols.txt", "r") as f:
        protocols = [line.strip() for line in f if line.strip()]
    
    with open("/tmp/tokens.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    
    print("🔍 Проверяем покрытие иконок для всех активных элементов...")
    print(f"📊 Всего элементов: {len(chains)} сетей + {len(protocols)} протоколов + {len(tokens)} токенов = {len(chains) + len(protocols) + len(tokens)}")
    print()
    
    results = {
        "chains": {"total": len(chains), "frontend": 0, "api": 0, "missing": []},
        "protocols": {"total": len(protocols), "frontend": 0, "api": 0, "missing": []},
        "tokens": {"total": len(tokens), "frontend": 0, "api": 0, "missing": []}
    }
    
    for category, items in [("chains", chains), ("protocols", protocols), ("tokens", tokens)]:
        print(f"🔍 Проверяем {category} ({len(items)} элементов)...")
        
        for item in items:
            result = check_icon_exists(item, category)
            
            if result["frontend_exists"]:
                results[category]["frontend"] += 1
            if result["api_exists"]:
                results[category]["api"] += 1
            
            # Если нет ни на фронтенде, ни в API
            if not result["frontend_exists"] and not result["api_exists"]:
                results[category]["missing"].append(result)
            # Если есть в API, но нет на фронтенде - это нормально (fallback работает)
            elif not result["frontend_exists"] and result["api_exists"]:
                # Проверяем, работает ли API
                if test_api_icon(category, result["normalized"]):
                    pass  # API работает, fallback сработает
                else:
                    results[category]["missing"].append(result)
    
    # Выводим результаты
    print("\n📊 РЕЗУЛЬТАТЫ ПОКРЫТИЯ ИКОНОК:")
    print("=" * 50)
    
    total_missing = 0
    for category, data in results.items():
        print(f"\n{category.upper()}:")
        print(f"  Всего: {data['total']}")
        print(f"  На фронтенде: {data['frontend']} ({data['frontend']/data['total']*100:.1f}%)")
        print(f"  В API: {data['api']} ({data['api']/data['total']*100:.1f}%)")
        print(f"  Отсутствует: {len(data['missing'])} ({len(data['missing'])/data['total']*100:.1f}%)")
        
        if data['missing']:
            print(f"  ❌ Отсутствующие {category}:")
            for item in data['missing'][:10]:  # Показываем первые 10
                print(f"    - {item['name']} -> {item['normalized']}.png")
            if len(data['missing']) > 10:
                print(f"    ... и еще {len(data['missing']) - 10}")
        
        total_missing += len(data['missing'])
    
    print(f"\n🎯 ИТОГО:")
    total_items = sum(data['total'] for data in results.values())
    print(f"  Всего элементов: {total_items}")
    print(f"  Отсутствует иконок: {total_missing}")
    print(f"  Покрытие: {(total_items - total_missing)/total_items*100:.1f}%")
    
    if total_missing == 0:
        print("\n🎉 ОТЛИЧНО! Все иконки на месте!")
    else:
        print(f"\n⚠️  Нужно загрузить {total_missing} иконок")
    
    return results

if __name__ == "__main__":
    check_coverage()
