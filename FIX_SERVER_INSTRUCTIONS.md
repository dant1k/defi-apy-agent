# 🔧 Инструкция по исправлению API URL на сервере

## Проблема
Frontend на http://46.224.99.147:3000 показывает "Loading market data..." и "0 strategies", потому что использует `localhost:8000` вместо `http://46.224.99.147:8000`.

## Решение

Выполни эти команды на сервере:

```bash
# 1. Подключись к серверу
ssh root@46.224.99.147

# 2. Перейди в директорию проекта
cd /opt/defi-apy-agent

# 3. Проверь текущий .env
cat .env | grep NEXT_PUBLIC || echo "Переменные не найдены"

# 4. Обнови или создай переменные окружения
# Если .env существует:
sed -i 's|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://46.224.99.147:8000|g' .env
sed -i 's|NEXT_PUBLIC_API_BASE_URL=.*|NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000|g' .env

# Если переменных нет, добавь их:
if ! grep -q "NEXT_PUBLIC_API_URL" .env; then
    echo "NEXT_PUBLIC_API_URL=http://46.224.99.147:8000" >> .env
fi
if ! grep -q "NEXT_PUBLIC_API_BASE_URL" .env; then
    echo "NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000" >> .env
fi

# 5. Проверь что переменные установлены
echo "Проверка переменных:"
grep NEXT_PUBLIC .env

# 6. Проверь как frontend запущен
docker ps | grep frontend
ls -la *.yml

# 7. Пересобери frontend контейнер
# Вариант A: Если frontend в docker-compose.yml
docker compose build frontend
docker compose up -d --force-recreate frontend

# Вариант B: Если frontend запущен отдельным контейнером
# Найди имя контейнера и пересобери его:
# docker stop <frontend-container-name>
# docker rm <frontend-container-name>
# docker compose build frontend
# docker compose up -d frontend

# Вариант C: Если frontend в отдельном compose файле (docker-compose.prod.yml)
docker compose -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.prod.yml up -d --force-recreate frontend

# 8. Проверь логи (опционально)
docker compose logs -f frontend
```

## После исправления

1. Подожди 1-2 минуты пока frontend пересоберется
2. Обнови страницу http://46.224.99.147:3000
3. Данные должны загрузиться

## Проверка

После перезапуска проверь:
- Открой http://46.224.99.147:3000
- Открой DevTools (F12) → Network
- Убедись что запросы идут на http://46.224.99.147:8000
- Данные должны отображаться

