# Testing Guide for DEX Adapters

## Структура тестов

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_adapters.py          # Тесты адаптеров
│   ├── test_aptos_indexer.py     # Тесты Aptos Indexer
│   └── fixtures/
│       ├── __init__.py
│       ├── example_tx.json        # Пример fixture
│       └── tx_<version>.json      # Реальные fixtures
```

## Запуск тестов

```bash
cd backend
pytest tests/ -v
```

Или конкретный тест:
```bash
pytest tests/test_adapters.py::TestPancakeAptosAdapter -v
```

## Процесс разработки адаптера

### 1. Собрать реальные транзакции

Для каждого DEX нужно найти 3 реальные swap транзакции:
- Открой Aptos Explorer
- Найди swap транзакции для нужного DEX
- Скопируй transaction version

### 2. Запустить discovery

```bash
python scripts/discover_dex_fees.py <tx_version> <dex_slug>
```

Это создаст fixture в `tests/fixtures/tx_<version>.json`

### 3. Анализ fixture

Открой fixture и найди:
- Entry function (из transaction details)
- Fee recipient address (из activities)
- Fee movements (отдельные движения токенов)

### 4. Обновить адаптер

В `app/providers/adapters/<dex>_aptos_adapter.py`:

```python
def get_swap_entry_functions(self) -> List[str]:
    # Добавь реальные entry functions
    return ["0x1::dex::swap"]

def get_fee_recipient_address(self, pool_address: str) -> Optional[str]:
    # Верни fee recipient если найден
    return "0x789...fee_recipient"

def parse_fees_from_activities(self, activities, pool_address, token0, token1):
    # Реализуй логику поиска fees
    # ...
```

### 5. Написать тесты

В `tests/test_adapters.py` добавь тесты на основе fixtures:

```python
def test_parse_fees_from_real_tx(self):
    fixture = load_fixture(123456789)  # Реальная tx
    activities = fixture["activities"]
    result = adapter.parse_fees_from_activities(...)
    assert result is not None
    assert result["fee_token0"] > 0
```

### 6. Запустить тесты

```bash
pytest tests/test_adapters.py::TestPancakeAptosAdapter::test_parse_fees_from_real_tx -v
```

## Примеры fixtures

Смотри `tests/fixtures/example_tx.json` для структуры.

## Интеграционные тесты

Для полного тестирования с реальным Indexer:

```bash
pytest tests/test_aptos_indexer.py -v -m integration
```

(Требует доступ к Aptos Indexer API)

