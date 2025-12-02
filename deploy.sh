#!/bin/bash
set -e

echo "🚀 Deploying DeFi APY Agent to Hetzner..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before continuing!${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    exit 1
fi

# Остановка старых контейнеров
echo -e "${GREEN}📦 Stopping old containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Сборка образов
echo -e "${GREEN}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Запуск контейнеров
echo -e "${GREEN}🚀 Starting containers...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Ожидание готовности сервисов
echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Проверка статуса
echo -e "${GREEN}📊 Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Проверка здоровья API
echo -e "${GREEN}🏥 Checking API health...${NC}"
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is healthy!${NC}"
else
    echo -e "${YELLOW}⚠️  API health check failed. Check logs with: docker-compose -f docker-compose.prod.yml logs api${NC}"
fi

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}📝 Useful commands:${NC}"
echo -e "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo -e "  - Stop: docker-compose -f docker-compose.prod.yml down"
echo -e "  - Restart: docker-compose -f docker-compose.prod.yml restart"

