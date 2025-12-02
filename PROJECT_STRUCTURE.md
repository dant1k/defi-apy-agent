# 📋 Структура проекта DeFi APY Agent

## 🎯 Общее описание

**DeFi APY Agent** - это комплексная платформа для анализа и подбора DeFi стратегий с использованием AI. Проект состоит из:
- **LangGraph агента** для интеллектуального подбора стратегий
- **FastAPI REST API** для доступа к данным
- **Next.js фронтенда** с современным UI
- **Системы сбора данных** из DeFiLlama, CoinGecko и других источников
- **Кэширования и агрегации** данных через Redis

---

## 🛠 Технологический стек

### Backend
- **Python 3.11+**
- **FastAPI** - REST API фреймворк
- **LangGraph** - агент для подбора стратегий
- **Redis** - кэширование данных
- **Uvicorn** - ASGI сервер
- **Pydantic** - валидация данных
- **Requests/Aiohttp** - HTTP клиенты

### Frontend
- **Next.js 14.2.5** - React фреймворк
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **Framer Motion** - анимации
- **Recharts** - графики и визуализация
- **Zustand** - state management

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Redis** - кэш и очереди
- **LangGraph Server** - сервер для агента

---

## 📁 Структура директорий

```
defi-apy-agent/
├── api/                          # FastAPI приложение
│   ├── main.py                  # Точка входа API
│   ├── cache.py                 # Redis кэширование
│   ├── dependencies.py          # FastAPI зависимости
│   ├── schemas.py               # Pydantic схемы
│   ├── routers/                 # API роутеры
│   │   ├── aggregator.py        # Агрегация стратегий
│   │   ├── strategies.py        # Поиск стратегий по токену
│   │   ├── mcp.py              # AI анализ через MCP
│   │   ├── cmc.py              # CoinMarketCap интеграция
│   │   └── cmc_cache.py        # Кэш CMC данных
│   └── static/                 # Статические файлы (иконки)
│
├── src/                         # Основная логика приложения
│   ├── agent/                  # LangGraph агент
│   │   └── graph.py           # Граф агента
│   ├── tools.py                # Инструменты для работы с DeFi
│   ├── analytics.py            # Аналитика стратегий
│   ├── coins.py                # Работа с токенами
│   ├── pool_index.py           # Индекс пулов
│   ├── nodes.py                # Узлы графа
│   ├── api.py                  # API клиент
│   ├── app.py                  # CLI приложение
│   └── utils/                  # Утилиты
│       ├── constants.py        # Константы
│       └── tokens.py           # Работа с токенами
│
├── collector/                   # Система сбора данных
│   ├── pipeline.py             # Основной пайплайн
│   ├── data_sources.py         # Источники данных
│   ├── defillama_extended.py   # Расширенный DeFiLlama клиент
│   ├── normalizer.py           # Нормализация данных
│   ├── storage.py              # Хранение в Redis
│   └── config.py               # Конфигурация
│
├── worker/                      # Фоновые задачи
│   └── updater.py              # Обновление данных
│
├── frontend/                    # Next.js приложение
│   ├── app/                    # App Router страницы
│   │   ├── page.tsx            # Главная (Dashboard)
│   │   ├── strategies/         # Страница стратегий
│   │   ├── trending/          # Трендовые стратегии
│   │   └── dashboard/         # Analytics Dashboard
│   ├── components/             # React компоненты
│   │   ├── home/              # Главная страница
│   │   ├── strategies/        # Стратегии
│   │   ├── ai/                # AI компоненты
│   │   ├── charts/            # Графики
│   │   ├── analytics/         # Аналитика
│   │   ├── filters/           # Фильтры
│   │   ├── market/            # Рыночные данные
│   │   ├── search/            # Поиск
│   │   └── navigation.tsx     # Навигация
│   ├── lib/                    # Утилиты
│   │   └── api.ts             # API клиент
│   └── public/                # Статические файлы
│
├── scripts/                     # Скрипты утилиты
│   └── [множество скриптов для работы с иконками]
│
├── tests/                       # Тесты
│   ├── unit_tests/            # Юнит тесты
│   └── integration_tests/     # Интеграционные тесты
│
├── docker-compose.yml          # Docker конфигурация
├── requirements.txt            # Python зависимости
├── pyproject.toml              # Python конфигурация
├── langgraph.json              # LangGraph конфигурация
└── README.md                   # Документация
```

---

## 🔌 API Endpoints

### Основные роутеры

#### `/` (Aggregator Router)
- `POST /refresh` - Принудительное обновление данных
- `GET /status` - Статус данных и кэша
- `GET /strategies` - Список стратегий с фильтрацией
  - Параметры: `chain`, `protocol`, `min_tvl`, `min_apy`, `sort`, `limit`, `offset`
- `GET /strategies/top` - Топ стратегий

#### `/strategies` (Strategies Router)
- `POST /strategies` - Поиск стратегий по токену
  - Body: `StrategyRequest` (token, preferences, force_refresh)
  - Response: `StrategyResponse` (best_strategy, alternatives, statistics)
- `GET /tokens` - Список доступных токенов
- `GET /analytics/new-pools` - Аналитика новых пулов

#### `/mcp` (MCP Router - AI Analysis)
- `GET /mcp/analyze-strategy/{strategy_id}` - Анализ стратегии
- `GET /mcp/market-insights` - Рыночные инсайты
- `POST /mcp/compare-strategies` - Сравнение стратегий
- `GET /mcp/predict-apy-trends` - Прогноз APY трендов
- `GET /mcp/risk-assessment/{strategy_id}` - Оценка рисков

#### `/cmc` (CoinMarketCap Router)
- `GET /cmc/tokens` - Топ токены из CMC
- `GET /cmc/chains` - Список сетей с иконками

#### Общие
- `GET /health` - Health check
- `GET /icons/{category}/{filename}` - Статические иконки

---

## 🧩 Основные модули

### 1. LangGraph Agent (`src/agent/graph.py`)
Граф агента для подбора стратегий:
- **prepare_state** - Нормализация входных данных
- **fetch_opportunities** - Получение стратегий из DeFiLlama
- **analyze_opportunities** - Фильтрация и анализ
- **format_response** - Формирование ответа

### 2. Tools (`src/tools.py`)
Инструменты для работы с DeFi:
- `get_opportunities()` - Получение стратегий по токену
- `analyze_strategies()` - Анализ и фильтрация
- `discover_new_pools()` - Поиск новых пулов
- `get_risk_description()` - Описание рисков

### 3. Collector Pipeline (`collector/pipeline.py`)
Сбор и обработка данных:
- `collect_and_store()` - Основной пайплайн
- Источники: DeFiLlama, CoinGecko
- Нормализация и вычисление метрик
- Сохранение в Redis

### 4. Cache (`api/cache.py`)
Redis кэширование:
- `StrategyCache` - Класс для работы с кэшем
- Методы: `get_latest_strategies()`, `get_strategy()`, `set_strategy()`
- TTL и управление устареванием

### 5. Storage (`collector/storage.py`)
Хранение стратегий:
- `StrategyStorage` - Класс для работы с Redis
- Методы: `store()`, `get_all()`, `compute_growth()`
- Структуры данных: sets, hashes, sorted sets

---

## 🎨 Frontend Компоненты

### Страницы (App Router)
- `/` - Analytics Dashboard (`app/page.tsx`)
- `/strategies` - Список стратегий
- `/trending` - Трендовые стратегии
- `/dashboard` - Расширенный дашборд

### Компоненты

#### Home (`components/home/`)
- `home-client.tsx` - Главный клиент
- `strategies-panel.tsx` - Панель стратегий
- `strategy-detail-modal.tsx` - Модалка деталей
- `analytics-panel.tsx` - Панель аналитики
- `types.ts` - TypeScript типы

#### AI (`components/ai/`)
- `ai-scoring.tsx` - AI оценка стратегий
- `ai-alerts.tsx` - AI уведомления
- `ai-suggestions.tsx` - AI рекомендации
- `strategy-explainer.tsx` - Объяснение стратегий

#### Charts (`components/charts/`)
- `advanced-charts.tsx` - Продвинутые графики
- `strategy-chart.tsx` - График стратегии
- `risk-matrix.tsx` - Матрица рисков
- `simple-charts.tsx` - Простые графики

#### Analytics (`components/analytics/`)
- `protocol-analytics.tsx` - Аналитика протоколов
- `trends-analysis.tsx` - Анализ трендов
- `risk-analysis.tsx` - Анализ рисков
- `data-export.tsx` - Экспорт данных

#### Market (`components/market/`)
- `market-overview.tsx` - Обзор рынка

#### Search (`components/search/`)
- `global-search.tsx` - Глобальный поиск
- `strategy-search.tsx` - Поиск стратегий

#### Filters (`components/filters/`)
- `advanced-filters.tsx` - Продвинутые фильтры

#### Interactive (`components/interactive/`)
- `watchlist.tsx` - Список наблюдения
- `wallet-connector.tsx` - Подключение кошелька

---

## 🔄 Потоки данных

### 1. Сбор данных
```
DeFiLlama API → Collector Pipeline → Normalizer → Storage (Redis)
```

### 2. Поиск стратегий
```
User Request → API → LangGraph Agent → Tools → DeFiLlama → Analysis → Response
```

### 3. Кэширование
```
API Request → Cache Check → Redis → If miss: Fetch → Store → Return
```

---

## 📊 Основные сущности

### Strategy (Стратегия)
```typescript
{
  id: string
  pool_id: string
  chain: string
  protocol: string
  apy: number
  tvl: number
  token_pair: string
  risk_level: "низкий" | "средний" | "высокий"
  ai_score: number
  tvl_growth_24h: number
  // ... другие поля
}
```

### Preferences (Предпочтения)
```typescript
{
  min_apy: number
  risk_level: string
  max_lockup_days: number
  min_tvl: number
  preferred_chains: string[]
  include_wrappers: boolean
}
```

### StrategyResponse
```typescript
{
  status: "ok" | "empty" | "error"
  token: string
  best_strategy: Strategy
  alternatives: Strategy[]
  statistics: {
    matched: number
    considered: number
  }
  warnings: string[]
}
```

---

## 🚀 Запуск проекта

### Backend
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Запуск LangGraph Server
langgraph dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Обычный режим
npm run dev:turbo    # Turbopack (быстрее)
```

### Docker
```bash
docker-compose up -d
```

### Переменные окружения
- `REDIS_URL` - URL Redis (по умолчанию: `redis://redis:6379/0`)
- `CMC_API_KEY` - API ключ CoinMarketCap (опционально)
- `TELEGRAM_BOT_TOKEN` - Токен Telegram бота (опционально)

---

## 📝 Ключевые особенности

1. **AI-анализ** - LangGraph агент для интеллектуального подбора стратегий
2. **Кэширование** - Redis для быстрого доступа к данным
3. **Реальное время** - Автообновление данных каждые 2 минуты
4. **Фильтрация** - По цепочкам, протоколам, APY, TVL, рискам
5. **Визуализация** - Графики, матрицы рисков, аналитика
6. **Масштабируемость** - Docker, микросервисная архитектура

---

## 🔧 Конфигурация

### LangGraph (`langgraph.json`)
```json
{
  "graphs": {
    "agent": "src.app:graph"
  }
}
```

### Docker Compose
- **redis** - Кэш и очереди
- **api** - FastAPI сервер
- **worker** - Фоновые задачи
- **mcp-server** - AI анализ сервер
- **dagster** - Data orchestration (опционально)
- **telegram-bot** - Telegram бот (опционально)

---

## 📚 Дополнительная документация

- `README.md` - Основная документация
- `ADVANCED_FEATURES.md` - Продвинутые функции
- `INTELLIGENCE_DASHBOARD.md` - AI дашборд

---

## 🎯 Текущее состояние

- ✅ LangGraph агент работает
- ✅ FastAPI API функционирует
- ✅ Next.js фронтенд запущен
- ✅ Система сбора данных активна
- ✅ Кэширование через Redis
- ❌ Раздел Airdrops удален (по запросу)

---

**Версия:** 2.0.0  
**Последнее обновление:** 2024-12-02

