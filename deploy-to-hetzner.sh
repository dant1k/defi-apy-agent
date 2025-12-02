#!/bin/bash
# Деплой на Hetzner сервер 46.224.99.147
set -e

SERVER_IP="46.224.99.147"
SERVER_USER="root"

echo "🚀 Deploying to Hetzner server: $SERVER_IP"

# Проверка SSH доступа
echo "📡 Checking SSH connection..."
if ! ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo 'Connection OK'" 2>/dev/null; then
    echo "❌ Cannot connect to server. Please check:"
    echo "   1. SSH ключ добавлен на сервер"
    echo "   2. Firewall разрешает SSH (порт 22)"
    echo "   3. IP адрес правильный: $SERVER_IP"
    exit 1
fi

echo "✅ SSH connection OK"

# Создание .env для продакшена
echo "📝 Creating production .env file..."
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
DOMAIN=${SERVER_IP}

# Python Path
PYTHONPATH=/app:/app/src
EOF

echo "📦 Preparing deployment..."

# Создание архива
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.env.local' \
    -czf deploy.tar.gz . 2>/dev/null || true

echo "📤 Uploading files to server..."
scp deploy.tar.gz $SERVER_USER@$SERVER_IP:/opt/
scp deploy.sh $SERVER_USER@$SERVER_IP:/opt/
scp docker-compose.prod.yml $SERVER_USER@$SERVER_IP:/opt/
scp .env.prod $SERVER_USER@$SERVER_IP:/opt/.env

echo "🔧 Setting up on server..."
ssh $SERVER_USER@$SERVER_IP << ENDSSH
set -e

echo "📦 Installing Docker if needed..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
    apt-get update
    apt-get install -y docker-compose-plugin || apt-get install -y docker-compose
fi

echo "📁 Setting up project directory..."
cd /opt
rm -rf defi-apy-agent
mkdir -p defi-apy-agent
cd defi-apy-agent

echo "📂 Extracting files..."
tar -xzf ../deploy.tar.gz
mv ../.env .env
chmod +x ../deploy.sh

echo "🔧 Configuring firewall..."
ufw allow 3000/tcp || true
ufw allow 8000/tcp || true
ufw allow 22/tcp || true

echo "🚀 Starting deployment..."
cd /opt
./deploy.sh

echo "✅ Deployment complete!"
echo "🌐 Frontend: http://${SERVER_IP}:3000"
echo "🔧 API: http://${SERVER_IP}:8000"
ENDSSH

# Очистка
rm -f deploy.tar.gz .env.prod

echo ""
echo "✅ Deployment to $SERVER_IP complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://${SERVER_IP}:3000"
echo "   API:      http://${SERVER_IP}:8000"
echo "   API Docs: http://${SERVER_IP}:8000/docs"
echo ""
echo "📊 Check status:"
echo "   ssh $SERVER_USER@$SERVER_IP 'cd /opt/defi-apy-agent && docker compose -f docker-compose.prod.yml ps'"
echo ""
echo "📝 View logs:"
echo "   ssh $SERVER_USER@$SERVER_IP 'cd /opt/defi-apy-agent && docker compose -f docker-compose.prod.yml logs -f'"

