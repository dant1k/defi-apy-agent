# Genora Terminal - DEX & Pool Metrics

Новый проект для терминала метрик DEX и Pool.

## Структура проекта

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core config, database, scheduler
│   │   ├── models/      # SQLAlchemy models
│   │   ├── providers/   # Data providers (DefiLlama, Dexscreener)
│   │   └── services/    # Business logic
│   └── main.py
├── frontend-terminal/    # Next.js frontend
│   ├── app/
│   └── components/
└── docker-compose.terminal.yml
```

## Быстрый старт

### 1. Настройка окружения

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend-terminal/.env.example frontend-terminal/.env
```

### 2. Запуск через Docker Compose

```bash
docker compose -f docker-compose.terminal.yml up --build
```

Сервисы будут доступны:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Postgres**: localhost:5432
- **Redis**: localhost:6379

### 3. Проверка

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## Разработка

### Backend (локально)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (локально)

```bash
cd frontend-terminal
npm install
npm run dev
```

## Следующие шаги

1. ✅ Repo bootstrap - **ГОТОВО**
2. ⏭️ DB schema - миграции для таблиц
3. ⏭️ Data provider интерфейс
4. ⏭️ DefiLlama интеграция
5. ⏭️ Dexscreener интеграция
6. ⏭️ Ingestion jobs
7. ⏭️ Redis cache
8. ⏭️ Backend API endpoints
9. ⏭️ Frontend skeleton pages
10. ⏭️ Frontend data layer
11. ⏭️ Charts
12. ⏭️ QA acceptance

