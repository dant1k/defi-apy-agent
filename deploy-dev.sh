#!/bin/bash
# Деплой на DEV окружение
set -e

echo "🚀 Deploying to DEV environment..."

# Проверка наличия .env файла
if [ ! -f .env.dev ]; then
    echo "⚠️  .env.dev file not found. Creating from .env.dev.example..."
    if [ -f .env.dev.example ]; then
        cp .env.dev.example .env.dev
        echo "⚠️  Please edit .env.dev file with your configuration before continuing!"
        exit 1
    else
        echo "❌ .env.dev.example not found!"
        exit 1
    fi
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    exit 1
fi

# Остановка старых контейнеров
echo "📦 Stopping old containers..."
docker-compose -f docker-compose.dev.yml down

# Сборка образов
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Запуск контейнеров
echo "🚀 Starting containers..."
docker-compose -f docker-compose.dev.yml up -d

# Ожидание готовности сервисов
echo "⏳ Waiting for services to be ready..."
sleep 10

# Проверка статуса
echo "📊 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

# Проверка здоровья API
echo "🏥 Checking API health..."
sleep 5
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ API is healthy!"
else
    echo "⚠️  API health check failed. Check logs with: docker-compose -f docker-compose.dev.yml logs api"
fi

echo "✅ DEV deployment complete!"
echo "📝 Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - Stop: docker-compose -f docker-compose.dev.yml down"
echo "  - Restart: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3001"
echo "   API:      http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"

