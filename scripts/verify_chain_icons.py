#!/usr/bin/env python3
"""
Проверка иконок сетей на соответствие
"""

import requests
import os
import hashlib
from typing import Dict, List

def get_file_hash(filepath: str) -> str:
    """Получаем хеш файла"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def check_chain_icons():
    """Проверяем иконки сетей"""
    print("🔍 Проверяем иконки сетей...")
    
    # Получаем список наших сетей
    try:
        response = requests.get("http://localhost:8000/strategies?min_tvl=1000000&limit=500", timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            chains = sorted(set(item["chain"] for item in items if item.get("chain")))
        else:
            print("Ошибка получения данных")
            return
    except Exception as e:
        print(f"Ошибка: {e}")
        return
    
    print(f"📊 Найдено сетей: {len(chains)}")
    print("")
    
    # Проверяем каждую иконку
    for chain in chains:
        filename = chain.upper().replace(" ", "").replace("-", "").replace(".", "") + ".png"
        api_path = f"api/static/icons/chains/{filename}"
        frontend_path = f"frontend/public/icons/chains/{filename}"
        
        if os.path.exists(api_path):
            file_size = os.path.getsize(api_path)
            file_hash = get_file_hash(api_path)
            print(f"✅ {chain} -> {filename} ({file_size} bytes, hash: {file_hash[:8]}...)")
        else:
            print(f"❌ {chain} -> {filename} (отсутствует)")

if __name__ == "__main__":
    check_chain_icons()
