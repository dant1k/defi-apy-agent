# Сбор реальных транзакций и доработка адаптеров

## Быстрый старт

### Вариант 1: Автоматический поиск и discovery

```bash
# Найти и проанализировать транзакции для PancakeSwap
python scripts/find_and_discover.py pancakeswap-amm 3

# Найти и проанализировать транзакции для AUX Exchange
python scripts/find_and_discover.py aux-exchange 3
```

Этот скрипт:
1. Найдет недавние swap транзакции через Indexer API
2. Запустит discovery для каждой
3. Сохранит fixtures

### Вариант 2: Ручной поиск в Explorer

1. Открой Aptos Explorer: https://explorer.aptoslabs.com/
2. Перейди на страницу DEX router:
   - PancakeSwap: https://explorer.aptoslabs.com/account/0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9
   - AUX Exchange: https://explorer.aptoslabs.com/account/0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8
3. Найди недавние swap транзакции
4. Скопируй transaction version
5. Запусти discovery:
   ```bash
   python scripts/discover_dex_fees.py <tx_version> <dex_slug>
   ```

## Процесс доработки адаптеров

### Шаг 1: Собрать fixtures

```bash
# Автоматически
python scripts/find_and_discover.py pancakeswap-amm 3

# Или вручную для конкретных транзакций
python scripts/discover_dex_fees.py 123456789 pancakeswap-amm
python scripts/discover_dex_fees.py 123456790 pancakeswap-amm
python scripts/discover_dex_fees.py 123456791 pancakeswap-amm
```

### Шаг 2: Анализ fixtures

```bash
# Валидация
python scripts/validate_fixture.py tests/fixtures/tx_123456789.json

# Агрегированный анализ всех fixtures для DEX
python scripts/analyze_fixtures.py pancakeswap-amm
```

### Шаг 3: Генерация адаптера

```bash
# Генерация кода из fixture
python scripts/update_adapter_from_fixture.py tests/fixtures/tx_123456789.json pancakeswap-amm
```

### Шаг 4: Доработка адаптера

Открой сгенерированный файл и обнови:

1. **Entry Functions** - из transaction details
2. **Fee Recipient** - из анализа fixtures
3. **Parse Logic** - по структуре activities

### Шаг 5: Тестирование

```bash
# Unit tests
pytest tests/test_adapters.py::TestPancakeAptosAdapter -v

# Интеграционный тест (требует реальный Indexer)
pytest tests/test_aptos_indexer.py -v
```

## Известные DEX конфигурации

### PancakeSwap
- Router: `0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9`
- Entry Functions:
  - `swap_exact_input`
  - `swap_exact_output`

### AUX Exchange
- Router: `0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8`
- Entry Functions:
  - `swap`

## Troubleshooting

### Нет транзакций найдено

1. Проверь, что DEX активен
2. Попробуй увеличить временной диапазон
3. Используй ручной поиск в Explorer

### Fixtures не содержат fee candidates

1. Fees могут быть в raw events (не в activities)
2. Fees могут быть включены в swap amounts
3. Fees могут храниться в pool contract

### Адаптер не находит fees

1. Проверь fee recipient address
2. Проверь asset types (могут быть в другом формате)
3. Проверь логику парсинга activities

