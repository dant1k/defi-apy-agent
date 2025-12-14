# 🚀 Быстрый старт - Genora Terminal

## 📁 Что мы создали

### Backend (FastAPI)
- **API endpoints**: `/api/v1/terminal/dexes`, `/api/v1/terminal/dexes/{slug}`, и т.д.
- **Data providers**: DefiLlama и Dexscreener интеграции
- **Scheduler**: Автоматическое обновление данных каждые 15/10 минут
- **Database**: Postgres с моделями Dex, Pool, DexMetricsDaily, PoolMetricsDaily
- **Cache**: Redis кеширование ответов API

### Frontend (Next.js)
- **Страницы**:
  - `/terminal/aptos/dex` - список DEXes
  - `/terminal/aptos/dex/[slug]` - детали DEX
  - `/terminal/aptos/dex/[slug]/pool/[id]` - детали Pool
- **Компоненты**: TerminalLayout, DataTable, Charts, Filters
- **Data layer**: React Query с debounce search

## 🎯 Как запустить и посмотреть

### 1. Запуск проекта

```bash
# Перейти в директорию проекта
cd /Users/Kos/defi-apy-agent

# Запустить все сервисы
docker compose -f docker-compose.terminal.yml up --build
```

### 2. Открыть в браузере

После запуска (подожди 1-2 минуты):

- **Frontend**: http://localhost:3000/terminal/aptos/dex
- **API документация**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### 3. Просмотр кода

**Backend API endpoints:**
```bash
# Список всех DEXes
curl http://localhost:8000/api/v1/terminal/dexes?chain=aptos

# Детали конкретного DEX
curl http://localhost:8000/api/v1/terminal/dexes/pancakeswap-v3

# Pools для DEX
curl http://localhost:8000/api/v1/terminal/dexes/pancakeswap-v3/pools
```

**Frontend страницы:**
- `frontend-terminal/app/terminal/aptos/dex/page.tsx` - список DEXes
- `frontend-terminal/app/terminal/aptos/dex/[dex_slug]/page.tsx` - детали DEX
- `frontend-terminal/components/` - все UI компоненты

**Backend код:**
- `backend/app/api/v1/terminal.py` - API endpoints
- `backend/app/providers/` - интеграции с внешними API
- `backend/app/jobs/` - scheduled jobs
- `backend/app/models/` - database модели

### 4. Проверка логов

```bash
# Логи API
docker compose -f docker-compose.terminal.yml logs -f api

# Логи frontend
docker compose -f docker-compose.terminal.yml logs -f web

# Все логи
docker compose -f docker-compose.terminal.yml logs -f
```

### 5. Остановка

```bash
docker compose -f docker-compose.terminal.yml down
```

## 📊 Что можно посмотреть

1. **Список DEXes** с TVL, Volume, Fees
2. **Детали DEX** с графиками за 30 дней
3. **Список Pools** для каждого DEX
4. **Детали Pool** с метриками
5. **Поиск и фильтрация** pools
6. **Charts** на recharts для визуализации данных

## 🔍 Структура файлов

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── models/          # Database models
│   ├── providers/       # DefiLlama, Dexscreener
│   ├── jobs/            # Scheduled jobs
│   └── core/            # Config, DB, Cache, Scheduler
└── main.py              # FastAPI app

frontend-terminal/
├── app/
│   └── terminal/        # Terminal pages
├── components/          # UI components
└── lib/                # API client, hooks
```

## ✅ Все готово к использованию!

