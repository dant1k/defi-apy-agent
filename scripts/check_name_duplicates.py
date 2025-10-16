#!/usr/bin/env python3
"""
Скрипт для проверки дубликатов названий в сетях, токенах и протоколах
"""

import os
import json
from pathlib import Path
from collections import defaultdict

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def get_file_names_from_directory(directory: Path, category: str):
    """Получить названия файлов из директории"""
    if not directory.exists():
        return []
    
    files = []
    for file_path in directory.glob("*.png"):
        # Убираем расширение .png
        name = file_path.stem
        files.append(name)
    
    return files

def normalize_name(name: str) -> str:
    """Нормализовать название для сравнения"""
    return name.lower().replace("-", "").replace("_", "").replace(" ", "").replace(".", "")

def find_duplicates_in_list(names: list, category: str):
    """Найти дубликаты в списке названий"""
    print(f"\n🔍 Checking {category} for name duplicates...")
    
    # Группируем по нормализованным названиям
    normalized_groups = defaultdict(list)
    
    for name in names:
        normalized = normalize_name(name)
        normalized_groups[normalized].append(name)
    
    # Ищем группы с более чем одним элементом
    duplicates = []
    for normalized, original_names in normalized_groups.items():
        if len(original_names) > 1:
            duplicates.append({
                'normalized': normalized,
                'originals': original_names
            })
    
    if duplicates:
        print(f"  ❌ Found {len(duplicates)} duplicate groups:")
        for i, dup in enumerate(duplicates, 1):
            print(f"    {i}. Normalized: '{dup['normalized']}'")
            print(f"       Originals: {', '.join(dup['originals'])}")
            print()
    else:
        print(f"  ✅ No duplicates found in {category}")
    
    return duplicates

def check_cross_category_duplicates():
    """Проверить дубликаты между категориями"""
    print(f"\n🔍 Checking for cross-category duplicates...")
    
    # Получаем все названия из всех категорий
    all_categories = {}
    
    for category in ['chains', 'tokens', 'protocols']:
        local_dir = ICONS_DIR / category
        backup_dir = BACKUP_DIR / category
        
        local_files = get_file_names_from_directory(local_dir, f"Local {category}")
        backup_files = get_file_names_from_directory(backup_dir, f"Backup {category}")
        
        all_files = list(set(local_files + backup_files))
        all_categories[category] = all_files
    
    # Ищем пересечения между категориями
    cross_duplicates = []
    
    categories = list(all_categories.keys())
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            cat1, cat2 = categories[i], categories[j]
            
            # Нормализуем названия для сравнения
            cat1_normalized = {normalize_name(name): name for name in all_categories[cat1]}
            cat2_normalized = {normalize_name(name): name for name in all_categories[cat2]}
            
            # Ищем пересечения
            common_normalized = set(cat1_normalized.keys()) & set(cat2_normalized.keys())
            
            if common_normalized:
                for normalized in common_normalized:
                    cross_duplicates.append({
                        'normalized': normalized,
                        'category1': cat1,
                        'name1': cat1_normalized[normalized],
                        'category2': cat2,
                        'name2': cat2_normalized[normalized]
                    })
    
    if cross_duplicates:
        print(f"  ❌ Found {len(cross_duplicates)} cross-category duplicates:")
        for i, dup in enumerate(cross_duplicates, 1):
            print(f"    {i}. Normalized: '{dup['normalized']}'")
            print(f"       {dup['category1']}: {dup['name1']}")
            print(f"       {dup['category2']}: {dup['name2']}")
            print()
    else:
        print(f"  ✅ No cross-category duplicates found")
    
    return cross_duplicates

def get_statistics():
    """Получить статистику по всем категориям"""
    print(f"\n📊 Statistics:")
    
    total_files = 0
    
    for category in ['chains', 'tokens', 'protocols']:
        local_dir = ICONS_DIR / category
        backup_dir = BACKUP_DIR / category
        
        local_files = get_file_names_from_directory(local_dir, f"Local {category}")
        backup_files = get_file_names_from_directory(backup_dir, f"Backup {category}")
        
        # Объединяем и убираем дубликаты
        all_files = list(set(local_files + backup_files))
        total_files += len(all_files)
        
        print(f"  {category.capitalize()}: {len(all_files)} unique names")
        print(f"    Local: {len(local_files)} files")
        print(f"    Backup: {len(backup_files)} files")
        print()
    
    print(f"  📊 Total unique names: {total_files}")

def main():
    print("🔍 Checking for name duplicates across all categories...")
    
    # Получаем статистику
    get_statistics()
    
    total_duplicates = 0
    total_cross_duplicates = 0
    
    # Проверяем дубликаты внутри каждой категории
    for category in ['chains', 'tokens', 'protocols']:
        local_dir = ICONS_DIR / category
        backup_dir = BACKUP_DIR / category
        
        local_files = get_file_names_from_directory(local_dir, f"Local {category}")
        backup_files = get_file_names_from_directory(backup_dir, f"Backup {category}")
        
        # Объединяем и убираем дубликаты
        all_files = list(set(local_files + backup_files))
        
        # Ищем дубликаты внутри категории
        duplicates = find_duplicates_in_list(all_files, category)
        total_duplicates += len(duplicates)
    
    # Проверяем дубликаты между категориями
    cross_duplicates = check_cross_category_duplicates()
    total_cross_duplicates = len(cross_duplicates)
    
    # Итоговая статистика
    print(f"\n📊 Duplicate Summary:")
    print(f"  Internal duplicates: {total_duplicates} groups")
    print(f"  Cross-category duplicates: {total_cross_duplicates} pairs")
    
    if total_duplicates > 0 or total_cross_duplicates > 0:
        print(f"\n💡 Recommendation: Consider renaming duplicates to avoid confusion")
    else:
        print(f"\n✅ No name duplicates found! Great organization!")

if __name__ == "__main__":
    main()

