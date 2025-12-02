#!/bin/bash
# Автоматическое исправление деплоя на сервере Hetzner
set -e

SERVER_IP="46.224.99.147"
SERVER_USER="root"

echo "🚀 Автоматическое исправление деплоя на сервере $SERVER_IP..."

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
set -e

echo "📦 Шаг 1: Удаление старой папки..."
cd /opt
rm -rf defi-apy-agent

echo "📥 Шаг 2: Клонирование репозитория..."
git clone https://github.com/dant1k/defi-apy-agent.git
cd defi-apy-agent
git checkout feature/dashboard-redesign

echo "⚙️  Шаг 3: Настройка .env..."
cp .env.example .env

# Автоматически настраиваем .env
cat >> .env << EOF

# Auto-configured for server
NEXT_PUBLIC_API_URL=http://46.224.99.147:8000
NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000
EOF

echo "🔧 Шаг 4: Настройка firewall..."
ufw allow 3000/tcp || true
ufw allow 8000/tcp || true
ufw allow 22/tcp || true

echo "🚀 Шаг 5: Запуск деплоя..."
chmod +x deploy.sh
docker compose -f docker-compose.prod.yml down || true
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "✅ Деплой завершен!"
echo "🌐 Frontend: http://46.224.99.147:3000"
echo "🔧 API: http://46.224.99.147:8000"
echo ""
echo "📊 Проверка статуса:"
sleep 5
docker compose -f docker-compose.prod.yml ps

ENDSSH

echo ""
echo "✅ Все готово! Приложение должно быть доступно:"
echo "   Frontend: http://46.224.99.147:3000"
echo "   API: http://46.224.99.147:8000"

