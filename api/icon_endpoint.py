
@app.get("/icons/{category}/{filename}")
async def get_icon(category: str, filename: str):
    """Получить иконку из backup или скачать из CoinGecko"""
    icon_path = f"api/static/icons/{category}/{filename}"
    
    # Если есть локально - отдаем
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/png")
    
    # Иначе скачиваем из CoinGecko (можно добавить логику)
    return {"error": "Icon not found"}
