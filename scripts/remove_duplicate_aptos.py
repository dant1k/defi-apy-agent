#!/usr/bin/env python3
"""
Скрипт для удаления дубликата APTOS (верхний)
"""

import os
from pathlib import Path

# Настройки
ICONS_DIR = Path("frontend/public/icons")
BACKUP_DIR = Path("api/static/icons")

def remove_duplicate_aptos():
    """Удалить дубликат APTOS (верхний)"""
    print("🗑️ Removing duplicate APTOS (uppercase)...")
    
    removed_count = 0
    
    # Удаляем из локальных иконок
    local_aptos_path = ICONS_DIR / "chains" / "APTOS.png"
    if local_aptos_path.exists():
        local_aptos_path.unlink()
        print(f"✓ Removed local: {local_aptos_path}")
        removed_count += 1
    
    # Удаляем из backup иконок
    backup_aptos_path = BACKUP_DIR / "chains" / "APTOS.png"
    if backup_aptos_path.exists():
        backup_aptos_path.unlink()
        print(f"✓ Removed backup: {backup_aptos_path}")
        removed_count += 1
    
    # Проверяем, что Aptos (правильный) остался
    local_aptos_correct = ICONS_DIR / "chains" / "Aptos.png"
    backup_aptos_correct = BACKUP_DIR / "chains" / "Aptos.png"
    
    if local_aptos_correct.exists():
        print(f"✅ Correct 'Aptos' (local) remains: {local_aptos_correct}")
    elif backup_aptos_correct.exists():
        print(f"✅ Correct 'Aptos' (backup) remains: {backup_aptos_correct}")
    else:
        print(f"❌ Warning: No correct 'Aptos' found!")
    
    print(f"📊 Removed {removed_count} duplicate APTOS files")
    return removed_count

def main():
    print("🚀 Removing duplicate APTOS (uppercase) to keep only Aptos (title case)...")
    
    removed_count = remove_duplicate_aptos()
    
    print(f"\n📊 Removal Summary:")
    print(f"  Total duplicate APTOS files removed: {removed_count}")
    
    if removed_count > 0:
        print(f"✅ Successfully removed {removed_count} duplicate APTOS files!")
        print(f"🎯 Now only 'Aptos' (title case) remains")
    else:
        print(f"ℹ️  No duplicate APTOS files found to remove")

if __name__ == "__main__":
    main()

