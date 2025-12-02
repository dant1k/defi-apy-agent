#!/bin/bash
# Быстрый деплой для Hetzner
set -e

SERVER_IP="${1:-}"
DOMAIN="${2:-}"

if [ -z "$SERVER_IP" ]; then
    echo "Usage: ./quick-deploy.sh <server-ip> [domain]"
    echo "Example: ./quick-deploy.sh 123.45.67.89 example.com"
    exit 1
fi

echo "🚀 Quick Deploy to Hetzner Server: $SERVER_IP"

# Создание .env для продакшена
cat > .env.prod << EOF
# Backend Configuration
REDIS_URL=redis://redis:6379/0
CMC_API_KEY=${CMC_API_KEY:-}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}

# Worker Configuration
AGGREGATOR_UPDATE_INTERVAL=900

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://${SERVER_IP}:8000
NEXT_PUBLIC_API_BASE_URL=http://${SERVER_IP}:8000

# Domain
DOMAIN=${DOMAIN:-${SERVER_IP}}

# Python Path
PYTHONPATH=/app:/app/src
EOF

echo "📦 Preparing deployment package..."

# Создание архива (исключая ненужные файлы)
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    -czf deploy.tar.gz .

echo "📤 Uploading to server..."
scp deploy.tar.gz root@${SERVER_IP}:/opt/
scp deploy.sh root@${SERVER_IP}:/opt/
scp docker-compose.prod.yml root@${SERVER_IP}:/opt/
scp .env.prod root@${SERVER_IP}:/opt/.env

echo "🔧 Setting up on server..."
ssh root@${SERVER_IP} << 'ENDSSH'
cd /opt
mkdir -p defi-apy-agent
cd defi-apy-agent
tar -xzf ../deploy.tar.gz
mv ../.env .env
chmod +x ../deploy.sh
../deploy.sh
ENDSSH

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://${SERVER_IP}:3000"
echo "🔧 API: http://${SERVER_IP}:8000"
if [ -n "$DOMAIN" ]; then
    echo "🌍 Domain: http://${DOMAIN}"
fi

