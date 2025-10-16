#!/usr/bin/env python3
"""
Скрипт для удаления дубликатов иконок
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

def remove_duplicates_in_directory(directory: Path, category: str):
    """Удалить дубликаты в директории"""
    print(f"\n🔍 Removing duplicates in {category}...")
    
    if not directory.exists():
        print(f"  → Directory {directory} does not exist")
        return 0
    
    # Собираем информацию о файлах
    hash_to_files = defaultdict(list)
    
    for file_path in directory.glob("*.png"):
        file_hash = get_file_hash(file_path)
        if file_hash:
            hash_to_files[file_hash].append(file_path)
    
    # Удаляем дубликаты (оставляем первый файл)
    removed_count = 0
    saved_space = 0
    
    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            # Сортируем файлы по имени для консистентности
            files.sort(key=lambda x: x.name)
            
            # Оставляем первый файл, удаляем остальные
            keep_file = files[0]
            remove_files = files[1:]
            
            print(f"  → Hash {file_hash[:8]}...: keeping {keep_file.name}")
            
            for file_to_remove in remove_files:
                try:
                    file_size = file_to_remove.stat().st_size
                    file_to_remove.unlink()
                    removed_count += 1
                    saved_space += file_size
                    print(f"    ✗ Removed: {file_to_remove.name} ({file_size} bytes)")
                except Exception as e:
                    print(f"    ❌ Failed to remove {file_to_remove.name}: {e}")
    
    if removed_count > 0:
        print(f"  📊 Removed {removed_count} files, saved {saved_space} bytes ({saved_space/1024:.1f} KB)")
    else:
        print(f"  ✅ No duplicates found in {category}")
    
    return removed_count, saved_space

def remove_cross_duplicates():
    """Удалить дубликаты между локальными и backup директориями"""
    print(f"\n🔍 Removing cross-directory duplicates...")
    
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
    
    # Удаляем дубликаты (приоритет локальным файлам)
    removed_count = 0
    saved_space = 0
    
    for file_hash in local_hashes:
        if file_hash in backup_hashes:
            local_info = local_hashes[file_hash]
            backup_info = backup_hashes[file_hash]
            
            try:
                file_size = backup_info['path'].stat().st_size
                backup_info['path'].unlink()
                removed_count += 1
                saved_space += file_size
                print(f"  ✗ Removed backup duplicate: {backup_info['category']}/{backup_info['name']} (duplicate of {local_info['category']}/{local_info['name']})")
            except Exception as e:
                print(f"  ❌ Failed to remove {backup_info['path']}: {e}")
    
    if removed_count > 0:
        print(f"  📊 Removed {removed_count} cross-duplicates, saved {saved_space} bytes ({saved_space/1024:.1f} KB)")
    else:
        print(f"  ✅ No cross-duplicates found")
    
    return removed_count, saved_space

def main():
    print("🗑️ Removing duplicate icons...")
    
    total_removed = 0
    total_saved = 0
    
    # Удаляем дубликаты внутри каждой директории
    for category in ['chains', 'tokens', 'protocols']:
        # Локальные дубликаты
        local_dir = ICONS_DIR / category
        removed, saved = remove_duplicates_in_directory(local_dir, f"Local {category}")
        total_removed += removed
        total_saved += saved
        
        # Backup дубликаты
        backup_dir = BACKUP_DIR / category
        removed, saved = remove_duplicates_in_directory(backup_dir, f"Backup {category}")
        total_removed += removed
        total_saved += saved
    
    # Удаляем дубликаты между директориями
    removed, saved = remove_cross_duplicates()
    total_removed += removed
    total_saved += saved
    
    # Итоговая статистика
    print(f"\n📊 Duplicate Removal Summary:")
    print(f"  Total files removed: {total_removed}")
    print(f"  Total space saved: {total_saved} bytes ({total_saved/1024:.1f} KB) ({total_saved/1024/1024:.1f} MB)")
    
    if total_removed > 0:
        print(f"\n✅ Successfully removed {total_removed} duplicate files!")
        print(f"💾 Saved {total_saved/1024/1024:.1f} MB of disk space")
    else:
        print(f"\n✅ No duplicates found to remove!")

if __name__ == "__main__":
    main()

