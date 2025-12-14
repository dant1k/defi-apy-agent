# Discovery Guide for DEX Fees

## Быстрый метод для создания адаптера под любой DEX

### Шаг 1: Найти реальную swap транзакцию

1. Открой Aptos Explorer для нужного DEX
2. Найди одну реальную swap транзакцию
3. Скопируй transaction version (число)

### Шаг 2: Запустить discovery скрипт

```bash
cd backend
python scripts/discover_dex_fees.py <transaction_version> <dex_slug>
```

Пример:
```bash
python scripts/discover_dex_fees.py 123456789 pancakeswap-amm
```

### Шаг 3: Анализ результатов

Скрипт покажет:
- Все fungible_asset_activities в транзакции
- Движения токенов
- Fee movements (если есть)

Сохранит fixture в `backend/tests/fixtures/tx_<version>.json`

### Шаг 4: Определить структуру fees

Ищи в activities:
1. **Fee recipient address** - адрес, который получает fees
2. **Fee store** - адрес пула, где хранятся fees
3. **Fee token movements** - отдельные движения fee токенов

### Шаг 5: Обновить DexAdapter

В `backend/app/providers/adapters/<dex>_aptos_adapter.py`:

1. **get_swap_entry_functions()** - добавь entry function идентификаторы
2. **get_fee_recipient_address()** - верни fee recipient адрес (если найден)
3. **parse_fees_from_activities()** - реализуй логику поиска fees

### Пример GraphQL запроса для Hasura Explorer

```graphql
query FeesDiscovery($v: bigint!) {
  fungible_asset_activities(
    where: { transaction_version: { _eq: $v } }
    order_by: { event_index: asc }
  ) {
    event_index
    owner_address
    asset_type
    type
    amount
  }
}
```

### Варианты обнаружения fees

**Вариант 1: Fee в event data**
- Fee лежит прямо в event data (поле `fee_amount`)
- Используй сырые events если activities не хватает

**Вариант 2: Fee как отдельное движение**
- Fee виден как отдельное движение в `fungible_asset_activities`
- Ищи delta по fee recipient или pool fee store
- Считай fee amount в токене

### Следующие шаги

1. Собери 3 реальные swap tx для каждого DEX
2. Запусти discovery для каждой
3. Сохрани fixtures
4. Доработай адаптеры по fixtures
5. Добавь unit tests

