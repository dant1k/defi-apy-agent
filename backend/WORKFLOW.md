# Workflow for Level 3 Implementation

## Полный процесс разработки адаптера для DEX

### Шаг 1: Найти swap транзакции

**Вариант A: Через Aptos Explorer (ручной)**
1. Открой https://explorer.aptoslabs.com/
2. Найди swap транзакции для нужного DEX
3. Скопируй transaction version

**Вариант B: Через скрипт (автоматический)**
```bash
python scripts/find_swap_transactions.py <dex_slug> [entry_function]
```

### Шаг 2: Запустить discovery

Для одной транзакции:
```bash
python scripts/discover_dex_fees.py <tx_version> <dex_slug>
```

Для нескольких транзакций:
```bash
python scripts/batch_discover.py <tx_version1> <tx_version2> <tx_version3> <dex_slug>
```

Это создаст fixtures в `tests/fixtures/tx_<version>.json`

### Шаг 3: Валидация fixtures

```bash
python scripts/validate_fixture.py tests/fixtures/tx_<version>.json
```

### Шаг 4: Генерация кода адаптера

```bash
python scripts/update_adapter_from_fixture.py tests/fixtures/tx_<version>.json <dex_slug>
```

Это создаст шаблон адаптера в `app/providers/adapters/<dex>_adapter_generated.py`

### Шаг 5: Доработка адаптера

1. Открой сгенерированный файл
2. Обнови `get_swap_entry_functions()` с реальными entry functions
3. Обнови `get_fee_recipient_address()` если найден
4. Доработай `parse_fees_from_activities()` по анализу fixtures
5. Переименуй файл в `<dex>_aptos_adapter.py`
6. Добавь в registry: `app/providers/adapters/__init__.py`

### Шаг 6: Тестирование

```bash
# Запустить тесты
pytest tests/test_adapters.py::Test<Dex>Adapter -v

# Или все тесты
pytest tests/ -v
```

### Шаг 7: Интеграция

Адаптер автоматически используется в:
- `AptosIndexerProvider.get_pool_real_fees()`
- `PoolRefreshJob` (Level 3 логика)

## Примеры команд

### PancakeSwap
```bash
# 1. Найти транзакции
python scripts/find_swap_transactions.py pancakeswap-amm

# 2. Discovery (используй найденные tx versions)
python scripts/discover_dex_fees.py 123456789 pancakeswap-amm
python scripts/discover_dex_fees.py 123456790 pancakeswap-amm
python scripts/discover_dex_fees.py 123456791 pancakeswap-amm

# 3. Валидация
python scripts/validate_fixture.py tests/fixtures/tx_123456789.json

# 4. Генерация адаптера
python scripts/update_adapter_from_fixture.py tests/fixtures/tx_123456789.json pancakeswap-amm

# 5. Тесты
pytest tests/test_adapters.py::TestPancakeAptosAdapter -v
```

### AUX Exchange
```bash
python scripts/discover_dex_fees.py <tx_version> aux-exchange
python scripts/update_adapter_from_fixture.py tests/fixtures/tx_<version>.json aux-exchange
```

## Структура файлов

```
backend/
├── scripts/
│   ├── discover_dex_fees.py          # Discovery одной транзакции
│   ├── batch_discover.py             # Discovery нескольких транзакций
│   ├── find_swap_transactions.py     # Поиск транзакций
│   ├── validate_fixture.py           # Валидация fixture
│   └── update_adapter_from_fixture.py # Генерация адаптера
├── tests/
│   └── fixtures/
│       └── tx_<version>.json         # Fixtures
└── app/
    └── providers/
        └── adapters/
            └── <dex>_aptos_adapter.py # Адаптеры
```

## Checklist для каждого DEX

- [ ] Найти 3 реальные swap транзакции
- [ ] Запустить discovery для каждой
- [ ] Валидировать fixtures
- [ ] Сгенерировать адаптер
- [ ] Доработать адаптер (entry functions, fee recipient, parsing)
- [ ] Написать тесты
- [ ] Добавить в registry
- [ ] Протестировать интеграцию

EOF

