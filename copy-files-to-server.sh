#!/bin/bash
# Скопировать измененные файлы на сервер

SERVER="root@46.224.99.147"
SERVER_DIR="/opt/defi-apy-agent"

echo "📋 Копирование файлов на сервер..."

# Копируем измененные файлы
scp frontend/components/home/home-client.tsx ${SERVER}:${SERVER_DIR}/frontend/components/home/
scp frontend/components/home/strategies-panel.tsx ${SERVER}:${SERVER_DIR}/frontend/components/home/

echo "✅ Файлы скопированы!"
echo ""
echo "📋 Теперь на сервере выполни:"
echo "cd /opt/defi-apy-agent"
echo "docker compose -f docker-compose.prod.yml build frontend"
echo "docker compose -f docker-compose.prod.yml up -d --force-recreate frontend"
