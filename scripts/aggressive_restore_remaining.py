#!/usr/bin/env python3
"""
Агрессивный скрипт для восстановления оставшихся недостающих иконок
"""

import os
import requests
import json
import time
from pathlib import Path

# Настройки
BACKUP_DIR = Path("api/static/icons")

def download_image(url: str, path: Path) -> bool:
    """Скачать изображение по URL"""
    try:
        if not url or not url.startswith('http'):
            return False
            
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {path.name}")
            return True
    except Exception as e:
        print(f"✗ Failed {path.name}: {e}")
    return False

def search_coingecko_aggressive(query: str):
    """Агрессивный поиск в CoinGecko"""
    try:
        # Пробуем разные варианты поиска
        search_variants = [
            query,
            query.lower(),
            query.upper(),
            query.replace("-", " "),
            query.replace(" ", "-"),
            query.replace("_", " "),
            query.replace(" ", "_"),
            query.replace("v2", "").replace("v3", "").replace("v4", "").strip(),
            query.replace("-v2", "").replace("-v3", "").replace("-v4", "").strip()
        ]
        
        for variant in search_variants:
            if not variant:
                continue
                
            response = requests.get("https://api.coingecko.com/api/v3/search", params={
                "query": variant
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("coins"):
                    for coin in data["coins"]:
                        coin_name = coin.get("name", "").lower()
                        coin_symbol = coin.get("symbol", "").upper()
                        variant_lower = variant.lower()
                        
                        # Более мягкое сравнение
                        if (variant_lower in coin_name or 
                            coin_name in variant_lower or
                            coin_symbol == variant.upper() or
                            abs(len(variant_lower) - len(coin_name)) <= 3):
                            return coin.get("large", "")
        
        return ""
    except Exception as e:
        print(f"Error in aggressive search for {query}: {e}")
    return ""

def restore_iota_token():
    """Восстановить токен IOTA"""
    print("🪙 Restoring IOTA token...")
    
    # Пробуем разные варианты поиска IOTA
    iota_variants = [
        "iota", "miota", "iota-tangle", "iota tangle", "IOTA", "MIOTA"
    ]
    
    for variant in iota_variants:
        print(f"🔍 Trying variant: {variant}")
        icon_url = search_coingecko_aggressive(variant)
        
        if icon_url:
            backup_path = BACKUP_DIR / "tokens" / "IOTA.png"
            if download_image(icon_url, backup_path):
                print(f"✅ Restored IOTA token")
                return True
            else:
                print(f"❌ Failed to download IOTA")
    
    print(f"❌ IOTA token not found")
    return False

def restore_missing_protocols_aggressive():
    """Агрессивное восстановление недостающих протоколов"""
    print("🏛️ Aggressive restoration of missing protocols...")
    
    # Список недостающих протоколов
    missing_protocols = [
        "3jane-options", "aave-v3", "aerodrome-v1", "alien-base-v2", "alien-base-v3",
        "anzen-v2", "apeswap-lending", "aptin-finance-v2", "arcadia-v2", "arrakis-v1",
        "arrakis-v2", "astar-network", "bancor-v3", "compound-v2", "curve-v2",
        "dydx-v4", "euler-v2", "gmx-v2", "kyber-network", "lido-v2",
        "makerdao", "pancakeswap-v3", "sushiswap-v3", "uniswap-v3", "yearn-finance-v2"
    ]
    
    restored_count = 0
    
    for protocol in missing_protocols:
        print(f"🔍 Aggressive search for {protocol}...")
        
        # Агрессивный поиск
        icon_url = search_coingecko_aggressive(protocol)
        
        if icon_url:
            # Нормализуем имя для файла
            import re
            file_name = re.sub(r'[^A-Z0-9]', '', protocol.upper())
            backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
            
            if download_image(icon_url, backup_path):
                restored_count += 1
                print(f"✅ Restored {protocol}")
            else:
                print(f"❌ Failed to download {protocol}")
        else:
            print(f"❌ Icon not found for {protocol}")
    
    print(f"📊 Restored {restored_count} protocol icons")
    return restored_count

def use_cmc_api_for_missing():
    """Использовать CoinMarketCap API для поиска недостающих иконок"""
    print("💰 Using CoinMarketCap API for missing icons...")
    
    # API ключ CoinMarketCap
    cmc_api_key = "4dc743a6ee7f4294a2d34f2969e37014"
    
    # Список для поиска
    search_items = [
        {"name": "IOTA", "type": "token"},
        {"name": "Aave", "type": "protocol"},
        {"name": "Compound", "type": "protocol"},
        {"name": "Curve", "type": "protocol"},
        {"name": "Uniswap", "type": "protocol"},
        {"name": "SushiSwap", "type": "protocol"},
        {"name": "PancakeSwap", "type": "protocol"},
        {"name": "Yearn Finance", "type": "protocol"},
        {"name": "MakerDAO", "type": "protocol"},
        {"name": "Kyber Network", "type": "protocol"}
    ]
    
    restored_count = 0
    
    for item in search_items:
        print(f"🔍 CMC search for {item['name']}...")
        
        try:
            headers = {
                'X-CMC_PRO_API_KEY': cmc_api_key,
                'Accept': 'application/json'
            }
            
            response = requests.get(
                "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
                headers=headers,
                params={'symbol': item['name'].upper()}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    # Получаем ID для детальной информации
                    coin_id = list(data['data'].keys())[0]
                    
                    # Получаем детальную информацию
                    detail_response = requests.get(
                        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info",
                        headers=headers,
                        params={'id': coin_id}
                    )
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('data'):
                            coin_info = list(detail_data['data'].values())[0]
                            logo_url = coin_info.get('logo')
                            
                            if logo_url:
                                if item['type'] == 'token':
                                    backup_path = BACKUP_DIR / "tokens" / f"{item['name']}.png"
                                else:
                                    import re
                                    file_name = re.sub(r'[^A-Z0-9]', '', item['name'].upper())
                                    backup_path = BACKUP_DIR / "protocols" / f"{file_name}.png"
                                
                                if download_image(logo_url, backup_path):
                                    restored_count += 1
                                    print(f"✅ Restored {item['name']} via CMC")
                                else:
                                    print(f"❌ Failed to download {item['name']}")
                            else:
                                print(f"❌ No logo URL for {item['name']}")
                        else:
                            print(f"❌ No detail data for {item['name']}")
                    else:
                        print(f"❌ Failed to get details for {item['name']}")
                else:
                    print(f"❌ No data for {item['name']}")
            else:
                print(f"❌ CMC API error for {item['name']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error with CMC API for {item['name']}: {e}")
        
        # Пауза между запросами
        time.sleep(1)
    
    print(f"📊 Restored {restored_count} icons via CMC API")
    return restored_count

def main():
    print("🚀 Aggressive restoration of remaining missing icons...")
    
    # Создаем директории
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    total_restored = 0
    
    # Восстанавливаем IOTA токен
    if restore_iota_token():
        total_restored += 1
    
    # Агрессивное восстановление протоколов
    total_restored += restore_missing_protocols_aggressive()
    
    # Используем CMC API
    total_restored += use_cmc_api_for_missing()
    
    print(f"\n📊 Aggressive Restoration Summary:")
    print(f"  Total icons restored: {total_restored}")
    
    if total_restored > 0:
        print(f"✅ Successfully restored {total_restored} missing icons!")
    else:
        print(f"❌ No icons were restored")

if __name__ == "__main__":
    main()

