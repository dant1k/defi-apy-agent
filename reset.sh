#!/bin/bash
set -e

echo "🚀 Resetting project to stable version (feature/stage1-ui-ux)..."

# 1️⃣ Проверка наличия репозитория
if [ ! -d .git ]; then
  echo "❌ This folder is not a Git repository."
  exit 1
fi

# 2️⃣ Получаем последние изменения
echo "🔄 Fetching latest from origin..."
git fetch origin

# 3️⃣ Переключаемся на стабильную ветку
echo "🌿 Checking out feature/stage1-ui-ux..."
git checkout feature/stage1-ui-ux || git checkout -b feature/stage1-ui-ux origin/feature/stage1-ui-ux

# 4️⃣ Сбрасываем изменения
echo "♻️ Resetting to remote version..."
git reset --hard origin/feature/stage1-ui-ux

# 5️⃣ Останавливаем Docker
echo "🧹 Stopping and cleaning Docker containers..."
docker-compose down -v

# 6️⃣ Удаляем мусор
echo "🧼 Cleaning node_modules and cache..."
rm -rf node_modules .next package-lock.json

# 7️⃣ Пересобираем
echo "⚙️ Rebuilding Docker containers..."
docker-compose up --build -d

echo "✅ Done! Project successfully reset to feature/stage1-ui-ux."
echo "🌐 Frontend: http://localhost:3000"
echo "🧠 Backend:  http://localhost:8000/docs"
