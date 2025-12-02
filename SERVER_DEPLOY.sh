#!/bin/bash
# Скрипт для выполнения НА СЕРВЕРЕ
# Скопируй и выполни на сервере: bash SERVER_DEPLOY.sh

set -e

echo "🚀 Deploying DeFi APY Agent on server..."

# Переход в рабочую директорию
cd /opt

# Удаление старой версии (если есть)
if [ -d "defi-apy-agent" ]; then
    echo "📦 Removing old version..."
    rm -rf defi-apy-agent
fi

# Клонирование репозитория
echo "📥 Cloning repository..."
git clone https://github.com/dant1k/defi-apy-agent.git
cd defi-apy-agent
git checkout feature/dashboard-redesign

# Настройка .env
echo "⚙️  Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and set:"
    echo "   NEXT_PUBLIC_API_URL=http://46.224.99.147:8000"
    echo "   NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

# Настройка firewall
echo "🔥 Configuring firewall..."
ufw allow 3000/tcp || true
ufw allow 8000/tcp || true
ufw allow 22/tcp || true

# Запуск деплоя
echo "🚀 Starting deployment..."
docker compose -f docker-compose.prod.yml up -d --build

# Ожидание готовности
echo "⏳ Waiting for services to start..."
sleep 10

# Проверка статуса
echo "📊 Service status:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "✅ Deployment complete!"
echo "🌐 Frontend: http://46.224.99.147:3000"
echo "🔧 API:      http://46.224.99.147:8000"
echo "📚 API Docs: http://46.224.99.147:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "   Restart:   docker compose -f docker-compose.prod.yml restart"
echo "   Stop:      docker compose -f docker-compose.prod.yml down"

