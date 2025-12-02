# 🚀 Деплой на Hetzner

Инструкция по развертыванию DeFi APY Agent на сервере Hetzner с использованием Docker.

## 📋 Требования

- Сервер Hetzner (Ubuntu 22.04 или новее)
- SSH доступ к серверу
- Домен (опционально, для Traefik)
- Минимум 2GB RAM, 2 CPU cores, 20GB диска

## 🔧 Подготовка сервера

### 1. Подключение к серверу

```bash
ssh root@your-server-ip
```

### 2. Установка Docker и Docker Compose

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
apt install docker-compose-plugin -y

# Проверка установки
docker --version
docker compose version
```

### 3. Установка дополнительных инструментов

```bash
# Git
apt install git -y

# Firewall (UFW)
apt install ufw -y
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

## 📦 Деплой приложения

### 1. Клонирование репозитория

```bash
cd /opt
git clone https://github.com/your-username/defi-apy-agent.git
cd defi-apy-agent
```

### 2. Настройка переменных окружения

```bash
# Копирование примера
cp .env.example .env

# Редактирование .env
nano .env
```

**Важные переменные для продакшена:**

```env
# Backend
REDIS_URL=redis://redis:6379/0
CMC_API_KEY=your_coinmarketcap_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Worker
AGGREGATOR_UPDATE_INTERVAL=900

# Frontend (важно для продакшена!)
NEXT_PUBLIC_API_URL=http://your-server-ip:8000
NEXT_PUBLIC_API_BASE_URL=http://your-server-ip:8000

# Domain (если используете Traefik)
DOMAIN=your-domain.com
```

### 3. Запуск деплоя

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запуск деплоя
./deploy.sh
```

Или вручную:

```bash
# Сборка и запуск
docker compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker compose -f docker-compose.prod.yml ps

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f
```

## 🌐 Настройка Nginx (опционально, если не используете Traefik)

### 1. Установка Nginx

```bash
apt install nginx -y
```

### 2. Создание конфигурации

```bash
nano /etc/nginx/sites-available/defi-apy-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Активация конфигурации

```bash
ln -s /etc/nginx/sites-available/defi-apy-agent /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 🔒 Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
apt install certbot python3-certbot-nginx -y

# Получение сертификата
certbot --nginx -d your-domain.com

# Автоматическое обновление
certbot renew --dry-run
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f worker
docker compose -f docker-compose.prod.yml logs -f frontend
```

### Проверка статуса

```bash
# Статус контейнеров
docker compose -f docker-compose.prod.yml ps

# Использование ресурсов
docker stats

# Проверка здоровья API
curl http://localhost:8000/health
```

## 🔄 Обновление приложения

```bash
cd /opt/defi-apy-agent

# Получение последних изменений
git pull origin main

# Пересборка и перезапуск
docker compose -f docker-compose.prod.yml up -d --build

# Очистка старых образов (опционально)
docker system prune -a
```

## 🛠️ Полезные команды

### Управление контейнерами

```bash
# Остановка
docker compose -f docker-compose.prod.yml down

# Перезапуск
docker compose -f docker-compose.prod.yml restart

# Перезапуск конкретного сервиса
docker compose -f docker-compose.prod.yml restart api

# Остановка с удалением volumes (⚠️ удалит данные Redis!)
docker compose -f docker-compose.prod.yml down -v
```

### Резервное копирование Redis

```bash
# Создание бэкапа
docker exec defi-apy-agent-redis-1 redis-cli SAVE
docker cp defi-apy-agent-redis-1:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb

# Восстановление
docker cp ./redis-backup-20240101.rdb defi-apy-agent-redis-1:/data/dump.rdb
docker compose -f docker-compose.prod.yml restart redis
```

## 🐛 Решение проблем

### Проблема: Контейнеры не запускаются

```bash
# Проверка логов
docker compose -f docker-compose.prod.yml logs

# Проверка портов
netstat -tulpn | grep -E '3000|8000|6379'

# Пересборка без кэша
docker compose -f docker-compose.prod.yml build --no-cache
```

### Проблема: Frontend не подключается к API

1. Проверьте переменные окружения в `.env`:
   ```env
   NEXT_PUBLIC_API_URL=http://your-server-ip:8000
   NEXT_PUBLIC_API_BASE_URL=http://your-server-ip:8000
   ```

2. Пересоберите frontend:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build frontend
   ```

### Проблема: Redis не сохраняет данные

```bash
# Проверка volumes
docker volume ls
docker volume inspect defi-apy-agent_redis-data

# Проверка прав доступа
docker exec defi-apy-agent-redis-1 ls -la /data
```

## 📈 Оптимизация производительности

### Настройка Redis

Добавьте в `docker-compose.prod.yml` для Redis:

```yaml
command: [
  "redis-server",
  "--appendonly", "yes",
  "--maxmemory", "1gb",
  "--maxmemory-policy", "allkeys-lru"
]
```

### Настройка Worker

Увеличьте интервал обновления для снижения нагрузки:

```env
AGGREGATOR_UPDATE_INTERVAL=1800  # 30 минут вместо 15
```

## 🔐 Безопасность

1. **Firewall**: Убедитесь, что открыты только необходимые порты
2. **SSH**: Используйте ключи вместо паролей
3. **Docker**: Не запускайте контейнеры от root
4. **Secrets**: Храните секреты в `.env`, не коммитьте в Git
5. **Updates**: Регулярно обновляйте систему и Docker образы

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker compose -f docker-compose.prod.yml logs`
2. Проверьте статус: `docker compose -f docker-compose.prod.yml ps`
3. Проверьте ресурсы: `docker stats`
4. Проверьте сеть: `docker network ls`

---

**Готово!** Ваше приложение должно быть доступно по адресу `http://your-server-ip:3000` или `http://your-domain.com`

