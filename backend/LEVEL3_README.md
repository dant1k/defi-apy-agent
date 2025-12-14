# Level 3: Aptos Indexer Integration

## Обзор

Level 3 реализует получение реальных fees для pools из событий блокчейна Aptos через GraphQL Indexer API.

## Архитектура

```
┌─────────────────┐
│  Pool Refresh   │
│      Job        │
└────────┬────────┘
         │
         ├─→ Level 2: Dexscreener (fees если есть)
         │
         └─→ Level 3: Aptos Indexer (реальные fees)
                    │
                    ├─→ AptosIndexerProvider
                    │   ├─→ fetch_swap_transactions_for_pool()
                    │   └─→ fetch_fungible_asset_activities_for_transaction()
                    │
                    ├─→ DexAdapter (per DEX)
                    │   ├─→ get_swap_entry_functions()
                    │   ├─→ get_fee_recipient_address()
                    │   └─→ parse_fees_from_activities()
                    │
                    └─→ PriceOracle
                        ├─→ DefiLlama
                        └─→ CoinGecko (fallback)
```

## Компоненты

### 1. AptosIndexerProvider
- **Файл**: `app/providers/aptos_indexer.py`
- **Функции**:
  - `verify_connection()` - проверка подключения
  - `fetch_swap_transactions_for_pool()` - поиск swap транзакций
  - `fetch_fungible_asset_activities_for_transaction()` - анализ транзакций
  - `get_pool_real_fees()` - получение реальных fees

### 2. DexAdapter System
- **Базовый класс**: `app/providers/adapters/base_adapter.py`
- **Реализации**:
  - `PancakeAptosAdapter` - PancakeSwap
  - `AuxAptosAdapter` - AUX Exchange
- **Registry**: `app/providers/adapters/__init__.py`

### 3. PriceOracle
- **Файл**: `app/providers/price_oracle.py`
- **Источники**: DefiLlama → CoinGecko
- **Поведение**: Возвращает `null` если цена недоступна (не приближает)

### 4. Database Schema
- **Поле**: `fees_source` в `pool_metrics_daily`
- **Значения**: `"dexscreener"` | `"aptos_indexer"` | `null`
- **Миграция**: `0d6389d6389c_add_fees_source_to_pool_metrics`

## Инструменты разработки

### Discovery
```bash
# Одна транзакция
python scripts/discover_dex_fees.py <tx_version> <dex_slug>

# Несколько транзакций
python scripts/batch_discover.py <tx1> <tx2> <tx3> <dex_slug>
```

### Поиск транзакций
```bash
python scripts/find_swap_transactions.py <dex_slug> [entry_function]
```

### Валидация
```bash
python scripts/validate_fixture.py tests/fixtures/tx_<version>.json
```

### Генерация адаптера
```bash
python scripts/update_adapter_from_fixture.py tests/fixtures/tx_<version>.json <dex_slug>
```

## Workflow

См. `WORKFLOW.md` для полного процесса разработки адаптера.

## Тестирование

```bash
# Все тесты
pytest tests/ -v

# Конкретный адаптер
pytest tests/test_adapters.py::TestPancakeAptosAdapter -v

# Aptos Indexer
pytest tests/test_aptos_indexer.py -v
```

## API

### Endpoints
- `GET /api/v1/terminal/dexes/{dex_slug}/pools` - возвращает `fees_source`
- `GET /api/v1/terminal/dexes/{dex_slug}/pools/{pool_id}` - возвращает `fees_source`

### Response Format
```json
{
  "fees_24h_usd": 1234.56,
  "fees_source": "aptos_indexer",
  ...
}
```

## UI

Бейдж `fees_source` отображается рядом с fees:
- **"Real"** (зеленый) - для `aptos_indexer`
- **"Estimate"** (желтый) - для `dexscreener`

## Документация

- `README_DISCOVERY.md` - гайд по discovery процессу
- `TESTING_GUIDE.md` - гайд по тестированию
- `WORKFLOW.md` - полный workflow разработки

## Статус

✅ **Готово**:
- Архитектура
- Инфраструктура
- Инструменты разработки
- Тесты
- UI

⏳ **В процессе**:
- Сбор реальных транзакций
- Доработка адаптеров по fixtures

## Ресурсы

- Aptos Explorer: https://explorer.aptoslabs.com/
- Hasura Explorer: https://api.mainnet.aptoslabs.com/v1/graphql
- Aptos Docs: https://aptos.dev/build/indexer/indexer-api

EOF

