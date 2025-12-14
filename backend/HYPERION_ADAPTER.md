# Hyperion DEX Adapter - Implementation Notes

## Источники информации

- **Документация**: https://docs.hyperion.xyz/
- **Aptos Explorer**: https://explorer.aptoslabs.com/

## Архитектура Hyperion

Hyperion - это AMM DEX на Aptos с concentrated liquidity (как Uniswap V3).

### Fee Structure

- Fee берется на уровне пула
- Fee видно как отдельное движение токена в `fungible_asset_activities`
- Fee почти всегда того же `asset_type` что `token_in`
- Fee amount меньше основного swap amount
- Fee owner_address ≠ user (обычно pool или fee vault)

## Реализация адаптера

### Логика parse_fees_from_activities()

1. **Группировка по asset_type**
   - Группируем все activities по типу токена

2. **Определение пользователя**
   - Пользователь = адрес с both withdraw и deposit (swap participant)
   - Исключаем pool address из user addresses

3. **Поиск основного swap amount**
   - Находим largest movement в каждой группе asset_type

4. **Поиск fee**
   - Маленький deposit (positive amount)
   - Не пользователю (not in user_addresses)
   - К pool или fee vault
   - Amount < 10% от main swap amount
   - Берем наименьший стабильный deposit

### Entry Functions

TODO: Обновить с реальными entry functions из документации или Explorer:
- Проверить: https://docs.hyperion.xyz/developer
- Найти router contract address
- Найти swap entry functions

### USD Конвертация

- Используется PriceOracle (DefiLlama → CoinGecko)
- Если цена недоступна → `fees_usd = null` (не приближаем)

## Тестирование

```bash
# Unit tests
pytest tests/test_hyperion_adapter.py -v

# С реальными транзакциями
python scripts/discover_dex_fees.py <tx_version> hyperion
```

## Checklist

- [x] Адаптер создан
- [x] Логика parse_fees_from_activities() реализована
- [x] Тесты написаны и проходят
- [x] Интегрирован в registry
- [ ] Найти реальные entry functions из документации
- [ ] Найти реальные swap транзакции (≥10)
- [ ] Обновить fixtures с реальными данными
- [ ] Проверить стабильность fee detection
- [ ] Проверить отсутствие double count

## Ресурсы

- Документация: https://docs.hyperion.xyz/
- Aptos Explorer: https://explorer.aptoslabs.com/
- Discovery query: см. `README_DISCOVERY.md`

EOF

