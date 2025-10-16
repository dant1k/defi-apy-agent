#!/usr/bin/env python3
"""
Скрипт для проверки дубликатов иконок
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def get_file_hash(file_path: Path) -> str:
    """Получить MD5 хеш файла"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def get_file_size(file_path: Path) -> int:
    """Получить размер файла в байтах"""
    try:
        return file_path.stat().st_size
    except:
        return 0

def find_duplicates_in_directory(directory: Path, category: str):
    """Найти дубликаты в директории"""
    print(f"\n🔍 Checking {category} for duplicates...")
    
    if not directory.exists():
        print(f"  → Directory {directory} does not exist")
        return
    
    # Собираем информацию о файлах
    file_info = {}
    hash_to_files = defaultdict(list)
    
    for file_path in directory.glob("*.png"):
        file_hash = get_file_hash(file_path)
        file_size = get_file_size(file_path)
        
        if file_hash:
            file_info[file_path.name] = {
                'path': file_path,
                'hash': file_hash,
                'size': file_size
            }
            hash_to_files[file_hash].append(file_path.name)
    
    # Ищем дубликаты
    duplicates = []
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            duplicates.append({
                'hash': file_hash,
                'files': files,
                'size': file_info[files[0]]['size']
            })
    
    if duplicates:
        print(f"  ❌ Found {len(duplicates)} duplicate groups:")
        total_wasted_space = 0
        
        for i, dup in enumerate(duplicates, 1):
            wasted_space = dup['size'] * (len(dup['files']) - 1)
            total_wasted_space += wasted_space
            
            print(f"    {i}. Hash: {dup['hash'][:8]}...")
            print(f"       Size: {dup['size']} bytes")
            print(f"       Files: {', '.join(dup['files'])}")
            print(f"       Wasted space: {wasted_space} bytes")
            print()
        
        print(f"  📊 Total wasted space: {total_wasted_space} bytes ({total_wasted_space/1024:.1f} KB)")
    else:
        print(f"  ✅ No duplicates found in {category}")
    
    return duplicates

def find_duplicates_between_directories():
    """Найти дубликаты между локальными и backup директориями"""
    print(f"\n🔍 Checking for duplicates between local and backup directories...")
    
    # Собираем хеши из локальных директорий
    local_hashes = {}
    for category in ['chains', 'tokens', 'protocols']:
        local_dir = ICONS_DIR / category
        if local_dir.exists():
            for file_path in local_dir.glob("*.png"):
                file_hash = get_file_hash(file_path)
                if file_hash:
                    local_hashes[file_hash] = {
                        'path': file_path,
                        'category': category,
                        'name': file_path.name
                    }
    
    # Собираем хеши из backup директорий
    backup_hashes = {}
    for category in ['chains', 'tokens', 'protocols']:
        backup_dir = BACKUP_DIR / category
        if backup_dir.exists():
            for file_path in backup_dir.glob("*.png"):
                file_hash = get_file_hash(file_path)
                if file_hash:
                    backup_hashes[file_hash] = {
                        'path': file_path,
                        'category': category,
                        'name': file_path.name
                    }
    
    # Ищем пересечения
    cross_duplicates = []
    for file_hash in local_hashes:
        if file_hash in backup_hashes:
            local_info = local_hashes[file_hash]
            backup_info = backup_hashes[file_hash]
            
            cross_duplicates.append({
                'hash': file_hash,
                'local': local_info,
                'backup': backup_info
            })
    
    if cross_duplicates:
        print(f"  ❌ Found {len(cross_duplicates)} cross-duplicates:")
        total_wasted_space = 0
        
        for i, dup in enumerate(cross_duplicates, 1):
            local_size = get_file_size(dup['local']['path'])
            total_wasted_space += local_size
            
            print(f"    {i}. Hash: {dup['hash'][:8]}...")
            print(f"       Local: {dup['local']['category']}/{dup['local']['name']}")
            print(f"       Backup: {dup['backup']['category']}/{dup['backup']['name']}")
            print(f"       Size: {local_size} bytes")
            print()
        
        print(f"  📊 Total wasted space: {total_wasted_space} bytes ({total_wasted_space/1024:.1f} KB)")
    else:
        print(f"  ✅ No cross-duplicates found")
    
    return cross_duplicates

def get_directory_stats():
    """Получить статистику по директориям"""
    print(f"\n📊 Directory Statistics:")
    
    total_files = 0
    total_size = 0
    
    for category in ['chains', 'tokens', 'protocols']:
        local_dir = ICONS_DIR / category
        backup_dir = BACKUP_DIR / category
        
        local_files = 0
        local_size = 0
        if local_dir.exists():
            for file_path in local_dir.glob("*.png"):
                local_files += 1
                local_size += get_file_size(file_path)
        
        backup_files = 0
        backup_size = 0
        if backup_dir.exists():
            for file_path in backup_dir.glob("*.png"):
                backup_files += 1
                backup_size += get_file_size(file_path)
        
        total_files += local_files + backup_files
        total_size += local_size + backup_size
        
        print(f"  {category.capitalize()}:")
        print(f"    Local: {local_files} files, {local_size/1024:.1f} KB")
        print(f"    Backup: {backup_files} files, {backup_size/1024:.1f} KB")
        print(f"    Total: {local_files + backup_files} files, {(local_size + backup_size)/1024:.1f} KB")
        print()
    
    print(f"  📊 Grand Total: {total_files} files, {total_size/1024:.1f} KB ({total_size/1024/1024:.1f} MB)")

def main():
    print("🔍 Checking for duplicate icons...")
    
    # Статистика директорий
    get_directory_stats()
    
    # Проверяем дубликаты внутри каждой директории
    all_duplicates = []
    
    for category in ['chains', 'tokens', 'protocols']:
        # Локальные дубликаты
        local_dir = ICONS_DIR / category
        local_dups = find_duplicates_in_directory(local_dir, f"Local {category}")
        if local_dups:
            all_duplicates.extend(local_dups)
        
        # Backup дубликаты
        backup_dir = BACKUP_DIR / category
        backup_dups = find_duplicates_in_directory(backup_dir, f"Backup {category}")
        if backup_dups:
            all_duplicates.extend(backup_dups)
    
    # Проверяем дубликаты между директориями
    cross_dups = find_duplicates_between_directories()
    
    # Итоговая статистика
    print(f"\n📊 Duplicate Summary:")
    print(f"  Internal duplicates: {len(all_duplicates)} groups")
    print(f"  Cross-directory duplicates: {len(cross_dups)} files")
    
    if all_duplicates or cross_dups:
        print(f"\n💡 Recommendation: Consider removing duplicates to save space")
    else:
        print(f"\n✅ No duplicates found! Great optimization!")

if __name__ == "__main__":
    main()

