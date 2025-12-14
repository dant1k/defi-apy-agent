#!/bin/bash
# Скрипт для обновления frontend на сервере после исправления localhost:8000

set -e

echo "🚀 Обновление frontend на сервере..."
echo ""

# Проверка подключения к серверу
echo "📡 Подключение к серверу..."
ssh root@46.224.99.147 << 'ENDSSH'
  set -e
  
  echo "📂 Переход в директорию проекта..."
  cd /opt/defi-apy-agent
  
  echo "🔄 Обновление кода с GitHub..."
  git pull origin main
  
  echo "🔍 Проверка переменных окружения..."
  if grep -q "NEXT_PUBLIC_API_URL=http://46.224.99.147:8000" .env && \
     grep -q "NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000" .env; then
    echo "✅ Переменные окружения настроены правильно"
  else
    echo "⚠️  ВНИМАНИЕ: Проверь переменные в .env файле!"
    echo "   Должно быть:"
    echo "   NEXT_PUBLIC_API_URL=http://46.224.99.147:8000"
    echo "   NEXT_PUBLIC_API_BASE_URL=http://46.224.99.147:8000"
    exit 1
  fi
  
  echo "🔨 Пересборка frontend..."
  docker compose -f docker-compose.prod.yml build frontend
  
  echo "🔄 Перезапуск frontend..."
  docker compose -f docker-compose.prod.yml up -d --force-recreate frontend
  
  echo "✅ Обновление завершено!"
  echo ""
  echo "⏱️  Подожди 1-2 минуты и обнови страницу:"
  echo "   http://46.224.99.147:3000"
  echo ""
  echo "📋 Для проверки логов выполни:"
  echo "   docker compose -f docker-compose.prod.yml logs -f frontend"
ENDSSH

echo ""
echo "✅ Готово! Проверь сайт через 1-2 минуты."

