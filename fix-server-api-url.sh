#!/bin/bash
# Скрипт для исправления API URL на продакшен сервере
set -e

SERVER_IP="46.224.99.147"
PROJECT_DIR="/opt/defi-apy-agent"

echo "🔧 Исправление API URL на сервере $SERVER_IP"
echo ""

echo "1️⃣ Подключение к серверу..."
ssh root@$SERVER_IP << 'EOF'
cd /opt/defi-apy-agent

echo "2️⃣ Проверка текущих переменных окружения..."
if [ -f .env ]; then
    echo "Текущий .env:"
    grep NEXT_PUBLIC .env || echo "NEXT_PUBLIC переменные не найдены"
else
    echo "⚠️  .env файл не найден, создаю из .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
    fi
fi

echo ""
echo "3️⃣ Обновление переменных окружения..."
sed -i 's|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://46.224.99.147:8000|g' .env
sed -i 's|NEXT_PUBLIC_API_BASE_URL=.*|NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000|g' .env

# Добавляем если их нет
if ! grep -q "NEXT_PUBLIC_API_URL" .env; then
    echo "NEXT_PUBLIC_API_URL=http://46.224.99.147:8000" >> .env
fi
if ! grep -q "NEXT_PUBLIC_API_BASE_URL" .env; then
    echo "NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000" >> .env
fi

echo ""
echo "4️⃣ Проверка обновленных переменных..."
echo "Обновленный .env:"
grep NEXT_PUBLIC .env

echo ""
echo "5️⃣ Пересборка frontend контейнера..."
# Используем docker-compose.prod.yml если есть, иначе docker-compose.yml
if [ -f docker-compose.prod.yml ]; then
    docker-compose -f docker-compose.prod.yml build frontend
    COMPOSE_FILE="docker-compose.prod.yml"
else
    docker-compose build frontend
    COMPOSE_FILE="docker-compose.yml"
fi

echo ""
echo "6️⃣ Перезапуск frontend контейнера..."
if [ -f docker-compose.prod.yml ]; then
    docker-compose -f docker-compose.prod.yml up -d --force-recreate frontend
else
    docker-compose up -d --force-recreate frontend
fi

echo ""
echo "✅ Готово! Frontend пересобран с правильным API URL"
echo "🌐 Проверь http://46.224.99.147:3000 через несколько секунд"
EOF

echo ""
echo "✅ Скрипт выполнен на сервере!"
echo "💡 Подожди 1-2 минуты пока frontend пересоберется"
echo "🌐 Затем проверь http://46.224.99.147:3000"

