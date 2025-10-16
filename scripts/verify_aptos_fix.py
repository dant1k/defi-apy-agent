#!/usr/bin/env python3
"""
Скрипт для проверки исправления дубликата APTOS
"""

import os
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def check_aptos_files():
    """Проверить файлы Aptos"""
    print("🔍 Checking Aptos files...")
    
    # Проверяем локальные файлы
    local_aptos_upper = ICONS_DIR / "chains" / "APTOS.png"
    local_aptos_correct = ICONS_DIR / "chains" / "Aptos.png"
    
    # Проверяем backup файлы
    backup_aptos_upper = BACKUP_DIR / "chains" / "APTOS.png"
    backup_aptos_correct = BACKUP_DIR / "chains" / "Aptos.png"
    
    print(f"📁 Local files:")
    print(f"  APTOS.png (upper): {'❌ EXISTS' if local_aptos_upper.exists() else '✅ NOT FOUND'}")
    print(f"  Aptos.png (correct): {'✅ EXISTS' if local_aptos_correct.exists() else '❌ NOT FOUND'}")
    
    print(f"📁 Backup files:")
    print(f"  APTOS.png (upper): {'❌ EXISTS' if backup_aptos_upper.exists() else '✅ NOT FOUND'}")
    print(f"  Aptos.png (correct): {'✅ EXISTS' if backup_aptos_correct.exists() else '❌ NOT FOUND'}")
    
    # Подсчитываем результаты
    upper_exists = local_aptos_upper.exists() or backup_aptos_upper.exists()
    correct_exists = local_aptos_correct.exists() or backup_aptos_correct.exists()
    
    return upper_exists, correct_exists

def check_all_aptos_variants():
    """Проверить все варианты Aptos в системе"""
    print(f"\n🔍 Checking all Aptos variants in the system...")
    
    # Ищем все файлы с aptos в названии
    aptos_files = []
    
    for root_dir in [ICONS_DIR, BACKUP_DIR]:
        if root_dir.exists():
            for file_path in root_dir.rglob("*aptos*"):
                aptos_files.append(file_path)
            for file_path in root_dir.rglob("*APTOS*"):
                aptos_files.append(file_path)
    
    if aptos_files:
        print(f"📊 Found {len(aptos_files)} Aptos-related files:")
        for file_path in aptos_files:
            print(f"  - {file_path}")
    else:
        print(f"❌ No Aptos-related files found")
    
    return aptos_files

def main():
    print("🔍 Verifying APTOS duplicate fix...")
    
    # Проверяем файлы Aptos
    upper_exists, correct_exists = check_aptos_files()
    
    # Проверяем все варианты
    all_aptos_files = check_all_aptos_variants()
    
    # Итоговый результат
    print(f"\n📊 Verification Summary:")
    print(f"  APTOS (upper) exists: {'❌ YES' if upper_exists else '✅ NO'}")
    print(f"  Aptos (correct) exists: {'✅ YES' if correct_exists else '❌ NO'}")
    print(f"  Total Aptos files: {len(all_aptos_files)}")
    
    if not upper_exists and correct_exists:
        print(f"\n✅ SUCCESS: Duplicate APTOS removed, correct Aptos remains!")
    elif upper_exists and not correct_exists:
        print(f"\n❌ ERROR: Only APTOS (upper) exists, correct Aptos missing!")
    elif upper_exists and correct_exists:
        print(f"\n⚠️  WARNING: Both APTOS (upper) and Aptos (correct) exist!")
    else:
        print(f"\n❌ ERROR: No Aptos files found!")

if __name__ == "__main__":
    main()

