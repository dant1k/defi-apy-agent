#!/bin/bash
# Run Alembic migrations
set -e

echo "🔄 Running database migrations..."

# Convert async URL to sync for Alembic
export DATABASE_URL_SYNC=$(echo $DATABASE_URL | sed 's/postgresql+asyncpg:\/\//postgresql:\/\//')

cd /app
alembic upgrade head

echo "✅ Migrations completed!"

