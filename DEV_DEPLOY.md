# 🚀 Деплой на DEV окружение

Инструкция по развертыванию DeFi APY Agent на DEV окружении.

## 📋 Варианты деплоя DEV

### Вариант 1: Локальный DEV (на твоей машине)

```bash
# 1. Переключись на dev ветку
git checkout dev
git pull origin dev

# 2. Создай .env.dev файл
cp .env.dev.example .env.dev
nano .env.dev  # Настрой переменные

# 3. Запусти деплой
chmod +x deploy-dev.sh
./deploy-dev.sh
```

**Доступ:**
- Frontend: http://localhost:3001
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Вариант 2: DEV сервер (отдельный сервер)

Если у тебя есть отдельный DEV сервер (например, dev.genora.com):

```bash
# На DEV сервере
ssh user@dev-server

# 1. Клонируй репозиторий
cd /opt
git clone https://github.com/dant1k/defi-apy-agent.git
cd defi-apy-agent
git checkout dev

# 2. Настрой .env.dev
cp .env.dev.example .env.dev
nano .env.dev
# Укажи:
# NEXT_PUBLIC_API_URL=http://dev-server-ip:8001
# NEXT_PUBLIC_API_BASE_URL=http://dev-server-ip:8001

# 3. Запусти деплой
chmod +x deploy-dev.sh
./deploy-dev.sh
```

### Вариант 3: DEV на том же сервере (другой порт)

Если хочешь запустить DEV и PROD на одном сервере:

```bash
# На сервере
cd /opt/defi-apy-agent-dev  # Отдельная папка для dev
git clone https://github.com/dant1k/defi-apy-agent.git .
git checkout dev

# Настрой .env.dev с другими портами
cp .env.dev.example .env.dev
nano .env.dev
# NEXT_PUBLIC_API_URL=http://server-ip:8001
# NEXT_PUBLIC_API_BASE_URL=http://server-ip:8001

# Запусти
./deploy-dev.sh
```

**Порты:**
- DEV: Frontend 3001, API 8001
- PROD: Frontend 3000, API 8000

## 🔧 Управление DEV окружением

### Просмотр логов
```bash
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f api
```

### Остановка
```bash
docker-compose -f docker-compose.dev.yml down
```

### Перезапуск
```bash
docker-compose -f docker-compose.dev.yml restart
docker-compose -f docker-compose.dev.yml restart frontend
```

### Обновление кода
```bash
git pull origin dev
docker-compose -f docker-compose.dev.yml up -d --build
```

## 📝 Отличия DEV от PROD

| Параметр | DEV | PROD |
|----------|-----|------|
| Frontend порт | 3001 | 3000 |
| API порт | 8001 | 8000 |
| Redis volume | redis-data-dev | redis-data |
| Docker compose | docker-compose.dev.yml | docker-compose.prod.yml |
| Ветка Git | dev | main |
| .env файл | .env.dev | .env |

## 🧪 Тестирование на DEV

После деплоя на DEV:

1. **Проверь Frontend:**
   - Открой http://localhost:3001 (или dev-server:3001)
   - Проверь все страницы
   - Проверь API запросы

2. **Проверь API:**
   - Открой http://localhost:8001/docs
   - Протестируй endpoints
   - Проверь health: http://localhost:8001/health

3. **Проверь Worker:**
   - Посмотри логи: `docker-compose -f docker-compose.dev.yml logs worker`
   - Убедись, что данные обновляются

## 🚀 После тестирования на DEV

Если все работает на DEV:

1. Смержь `dev` в `main`:
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

2. Задеплой на PROD сервер:
   ```bash
   # На PROD сервере
   git checkout main
   git pull origin main
   ./deploy.sh  # или docker-compose -f docker-compose.prod.yml up -d --build
   ```

---

**Готово!** Теперь у тебя есть отдельное DEV окружение для тестирования перед продакшеном.

