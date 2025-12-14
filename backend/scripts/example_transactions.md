# Example Transactions for Discovery

## Как использовать

1. Найди реальные swap транзакции в Aptos Explorer:
   - https://explorer.aptoslabs.com/
   - Поиск по DEX адресам или entry functions

2. Скопируй transaction version или URL

3. Запусти discovery:
   ```bash
   python scripts/discover_from_explorer.py <tx_version_or_url> <dex_slug>
   ```

## Известные DEX на Aptos

### PancakeSwap
- **Router**: `0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9`
- **Entry Functions**:
  - `swap_exact_input`
  - `swap_exact_output`
- **Explorer**: https://explorer.aptoslabs.com/account/0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfeab94f9

### AUX Exchange
- **Router**: `0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8`
- **Entry Functions**:
  - `swap`
- **Explorer**: https://explorer.aptoslabs.com/account/0xbd35135844473187163ca197ca93b2ab014370587bb0e3b26a3bc4d5190f77c8

### ThalaSwap
- **Router**: `0x48271d39d0b05bd6efca8d79b2d02f5e3a3e0a0e0e0e0e0e0e0e0e0e0e0e0e0`
- **Entry Functions**: (to be discovered)

### LiquidSwap
- **Router**: (to be discovered)
- **Entry Functions**: (to be discovered)

## Примеры команд

```bash
# PancakeSwap
python scripts/discover_from_explorer.py <tx_version> pancakeswap-amm

# AUX Exchange
python scripts/discover_from_explorer.py <tx_version> aux-exchange

# Batch discovery
python scripts/batch_discover.py <tx1> <tx2> <tx3> pancakeswap-amm
```

## Где найти транзакции

1. **Aptos Explorer**: https://explorer.aptoslabs.com/
   - Перейди на страницу DEX router
   - Найди недавние swap транзакции
   - Скопируй transaction version

2. **DEX Frontend**:
   - Открой DEX веб-сайт
   - Выполни тестовый swap
   - Скопируй transaction hash/version

3. **Indexer API** (программно):
   ```bash
   python scripts/find_swap_transactions.py <dex_slug>
   ```

## После discovery

1. Проверь fixture:
   ```bash
   python scripts/validate_fixture.py tests/fixtures/tx_<version>.json
   ```

2. Сгенерируй адаптер:
   ```bash
   python scripts/update_adapter_from_fixture.py tests/fixtures/tx_<version>.json <dex_slug>
   ```

3. Доработай адаптер и протестируй

