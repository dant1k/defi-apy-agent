#!/usr/bin/env python3
"""
Тест endpoints для иконок
"""

import requests
import json

def test_icon_endpoint(url, description):
    """Тестировать endpoint иконки"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print(f"✓ {description}: {url} (200, {content_type})")
                return True
            else:
                print(f"? {description}: {url} (200, {content_type}) - не изображение")
                return False
        else:
            print(f"✗ {description}: {url} ({response.status_code})")
            return False
    except Exception as e:
        print(f"✗ {description}: {url} (error: {e})")
        return False

def main():
    print("🧪 Testing icon endpoints...")
    
    # Тестируем локальные иконки (Next.js)
    print("\n📱 Local icons (Next.js):")
    local_tests = [
        ("http://localhost:3001/icons/chains/Ethereum.png", "Ethereum chain"),
        ("http://localhost:3001/icons/chains/Bitcoin.png", "Bitcoin chain"),
        ("http://localhost:3001/icons/tokens/BTC.png", "BTC token"),
        ("http://localhost:3001/icons/tokens/ETH.png", "ETH token"),
        ("http://localhost:3001/icons/protocols/AAVEV3.png", "AAVE protocol"),
    ]
    
    local_success = 0
    for url, desc in local_tests:
        if test_icon_endpoint(url, desc):
            local_success += 1
    
    # Тестируем бекенд иконки (FastAPI)
    print("\n🌐 Backend icons (FastAPI):")
    backend_tests = [
        ("http://localhost:8000/icons/chains/Arbitrum%20One.png", "Arbitrum chain"),
        ("http://localhost:8000/icons/chains/Blast.png", "Blast chain"),
        ("http://localhost:8000/icons/protocols/COMPOUNDV3.png", "Compound protocol"),
    ]
    
    backend_success = 0
    for url, desc in backend_tests:
        if test_icon_endpoint(url, desc):
            backend_success += 1
    
    # Результаты
    print(f"\n📊 Results:")
    print(f"Local icons: {local_success}/{len(local_tests)} working")
    print(f"Backend icons: {backend_success}/{len(backend_tests)} working")
    
    if local_success > 0:
        print("✅ Local icons are working!")
    if backend_success > 0:
        print("✅ Backend icons are working!")
    
    if local_success == 0 and backend_success == 0:
        print("❌ No icons are working!")

if __name__ == "__main__":
    main()
