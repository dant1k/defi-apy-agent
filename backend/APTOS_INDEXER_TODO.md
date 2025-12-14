# Aptos Indexer Integration (Level 3) - TODO

## Текущий статус

✅ Базовая структура создана:
- `AptosIndexerProvider` класс создан
- Интегрирован в `GenoraDataService`
- Добавлен в конфигурацию

## Что нужно доработать

### 1. Изучить реальную структуру Aptos Indexer API

**Варианты:**
- Aptos Indexer может использовать REST API вместо GraphQL
- Может быть несколько разных Indexer'ов (официальный, сторонние)
- Нужно проверить документацию: https://aptos.dev/guides/indexer

**Действия:**
- [ ] Найти актуальную документацию Aptos Indexer
- [ ] Определить правильный endpoint и формат запросов
- [ ] Протестировать запросы к реальному Indexer

### 2. Адаптировать GraphQL запросы

**Текущая структура (шаблон):**
```graphql
query GetSwapEvents($poolAddress: String!, $startTime: DateTime!, $endTime: DateTime!) {
    events(
        where: {
            type: {_eq: "0x1::dex::SwapEvent"}
            account_address: {_eq: $poolAddress}
            transaction_timestamp: {_gte: $startTime, _lte: $endTime}
        }
    ) {
        transaction_version
        transaction_timestamp
        data
        type
    }
}
```

**Нужно:**
- [ ] Уточнить реальную схему GraphQL (или REST API)
- [ ] Определить правильные типы событий для разных DEXes
- [ ] Адаптировать парсинг данных событий

### 3. Парсинг swap событий

**Разные DEXes на Aptos имеют разные структуры событий:**
- ThalaSwap: свой формат
- PancakeSwap: свой формат
- LiquidSwap: свой формат
- И т.д.

**Нужно:**
- [ ] Изучить структуру swap событий для каждого DEX
- [ ] Реализовать парсеры для каждого типа
- [ ] Извлекать: amount_in, amount_out, fee, fee_rate

### 4. Интеграция Price Oracle

**Для конвертации fees в USD нужен price oracle:**

**Варианты:**
- CoinGecko API
- CoinMarketCap API
- On-chain price oracle (если доступен)
- DefiLlama prices endpoint

**Нужно:**
- [ ] Создать PriceOracleProvider
- [ ] Интегрировать в AptosIndexerProvider
- [ ] Кэшировать цены (обновлять раз в минуту)
- [ ] Обрабатывать случаи, когда цена недоступна

### 5. Обновить Pool Refresh Job

**Текущая логика (Level 2):**
- Получает pools из Dexscreener
- Сохраняет fees если есть, иначе null

**Новая логика (Level 3):**
- Получает pools из Dexscreener (Level 2)
- Для каждого pool пытается получить реальные fees из Aptos Indexer
- Если Level 3 доступен → используем реальные fees
- Если Level 3 недоступен → используем Level 2 (Dexscreener) или null

**Нужно:**
- [ ] Обновить `refresh_pools_top_dexes_job`
- [ ] Добавить вызов `get_pool_real_fees()` для каждого pool
- [ ] Приоритизировать Level 3 над Level 2

### 6. Оптимизация производительности

**Проблемы:**
- Запросы к Indexer могут быть медленными
- Нужно обрабатывать много pools
- Rate limiting

**Решения:**
- [ ] Батчинг запросов (если API поддерживает)
- [ ] Кэширование результатов
- [ ] Обработка только активных pools (с volume > threshold)
- [ ] Асинхронная обработка

## Примеры использования

### После реализации:

```python
# В pool_refresh.py
service = GenoraDataService()

# Level 2: Получаем pools из Dexscreener
pools = await service.get_pools_for_dex("aptos", dex_slug)

for pool in pools:
    # Level 3: Пытаемся получить реальные fees
    real_fees = await service.get_pool_real_fees(
        pool_address=pool["address"],
        token0_address=pool["token0_address"],
        token1_address=pool["token1_address"]
    )
    
    if real_fees and real_fees.get("fees_24h_usd"):
        # Используем Level 3 (реальные fees)
        pool["fees_24h_usd"] = real_fees["fees_24h_usd"]
    elif pool.get("fees_24h_usd"):
        # Fallback на Level 2 (Dexscreener)
        pass
    else:
        # Нет данных - показываем "—"
        pool["fees_24h_usd"] = None
```

## Ресурсы

- Aptos Indexer Guide: https://aptos.dev/guides/indexer
- Aptos Events: https://aptos.dev/concepts/events
- Aptos SDK: https://github.com/aptos-labs/aptos-core

