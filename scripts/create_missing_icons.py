#!/usr/bin/env python3
"""
Создание недостающих иконок для выпадающих меню
"""

import os
import requests
import shutil
from PIL import Image, ImageDraw, ImageFont
import io

# Настройки
API_DIR = "api/static/icons"
FRONTEND_DIR = "frontend/public/icons"

def ensure_directories():
    """Создаем необходимые директории"""
    for category in ["chains", "protocols", "tokens"]:
        os.makedirs(f"{API_DIR}/{category}", exist_ok=True)
        os.makedirs(f"{FRONTEND_DIR}/{category}", exist_ok=True)

def create_text_icon(text, filename, category, size=(64, 64)):
    """Создаем текстовую иконку"""
    try:
        # Создаем изображение
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Пытаемся загрузить шрифт
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Получаем размер текста
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Центрируем текст
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Рисуем фон
        draw.rectangle([0, 0, size[0], size[1]], fill=(50, 50, 50, 255))
        
        # Рисуем текст
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Сохраняем
        api_path = f"{API_DIR}/{category}/{filename}"
        frontend_path = f"{FRONTEND_DIR}/{category}/{filename}"
        
        img.save(api_path, 'PNG')
        shutil.copy2(api_path, frontend_path)
        
        return True
    except Exception as e:
        print(f"Ошибка создания иконки {text}: {e}")
        return False

def download_known_icons():
    """Скачиваем известные иконки"""
    known_icons = {
        "protocols": {
            "ASTROPORT.png": "https://raw.githubusercontent.com/astroport-fi/astroport-assets/main/astroport-logo.png",
            "SILOV2.png": "https://raw.githubusercontent.com/silo-finance/brand-kit/main/silo-logo.png", 
            "SUSHISWAPV3.png": "https://raw.githubusercontent.com/sushiswap/icons/master/token/sushi.png"
        },
        "tokens": {
            "FRAX.png": "https://raw.githubusercontent.com/FraxFinance/frax-assets/main/frax-logo.png",
            "FTM.png": "https://raw.githubusercontent.com/Fantom-foundation/brand-resources/main/Logo/png/Fantom_Logo_Standard_Regular.png",
            "FUEL.png": "https://raw.githubusercontent.com/FuelLabs/fuel-assets/main/fuel-logo.png"
        }
    }
    
    downloaded = 0
    
    for category, icons in known_icons.items():
        for filename, url in icons.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    api_path = f"{API_DIR}/{category}/{filename}"
                    frontend_path = f"{FRONTEND_DIR}/{category}/{filename}"
                    
                    with open(api_path, 'wb') as f:
                        f.write(response.content)
                    shutil.copy2(api_path, frontend_path)
                    
                    print(f"✅ Скачано: {filename}")
                    downloaded += 1
                else:
                    print(f"❌ Ошибка скачивания {filename}: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка {filename}: {e}")
    
    return downloaded

def create_missing_icons():
    """Создаем недостающие иконки"""
    missing_icons = {
        "protocols": [
            ("ASTROPORT.png", "ASTRO"),
            ("SILOV2.png", "SILO"),
            ("SUSHISWAPV3.png", "SUSHI")
        ],
        "tokens": [
            ("$MYRO.png", "$MYRO"),
            ("20261231.png", "2026"),
            ("4.png", "4"),
            ("40AVAX.png", "40AVAX"),
            ("80RZR.png", "80RZR"),
            ("9SUSDC.png", "9SUSDC"),
            ("ACRV.png", "ACRV"),
            ("AI16Z.png", "AI16Z"),
            ("AIDAUSDC.png", "AIDA"),
            ("AIDAUSDT.png", "AIDA"),
            ("ATONE.png", "ATONE"),
            ("BNEO.png", "BNEO"),
            ("CUSDX.png", "CUSDX"),
            ("DYFI.png", "DYFI"),
            ("EPENDLE.png", "EPENDLE"),
            ("ESFDX.png", "ESFDX"),
            ("FBEETS.png", "FBEETS"),
            ("FRAXBP.png", "FRAXBP"),
            ("FRXUSD.png", "FRXUSD"),
            ("FXRP.png", "FXRP"),
            ("FXS.png", "FXS")
        ]
    }
    
    created = 0
    
    for category, icons in missing_icons.items():
        for filename, text in icons:
            if not os.path.exists(f"{API_DIR}/{category}/{filename}"):
                if create_text_icon(text, filename, category):
                    print(f"✅ Создано: {filename}")
                    created += 1
                else:
                    print(f"❌ Ошибка создания: {filename}")
    
    return created

def main():
    """Основная функция"""
    print("🔧 Создаем недостающие иконки для выпадающих меню...")
    
    ensure_directories()
    
    # Сначала пытаемся скачать известные иконки
    print("\n📥 Скачиваем известные иконки...")
    downloaded = download_known_icons()
    
    # Затем создаем текстовые иконки для остальных
    print("\n🎨 Создаем текстовые иконки...")
    created = create_missing_icons()
    
    print(f"\n🎉 ИТОГО:")
    print(f"✅ Скачано: {downloaded}")
    print(f"✅ Создано: {created}")
    print(f"📁 Все иконки сохранены в: {API_DIR}")

if __name__ == "__main__":
    main()
