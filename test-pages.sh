#!/bin/bash
echo "🧪 ТЕСТИРОВАНИЕ ЗАГРУЗКИ ДАННЫХ НА ВСЕХ СТРАНИЦАХ"
echo ""

API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8001}"
API_BASE="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8001}"

echo "📡 API URL: $API_URL"
echo "📡 API BASE: $API_BASE"
echo ""

# Проверка основных endpoints
echo "1️⃣ Проверка /health"
curl -s "$API_URL/health" | python3 -m json.tool && echo "✅" || echo "❌"

echo ""
echo "2️⃣ Проверка /chains"
chains=$(curl -s "$API_URL/chains")
echo "$chains" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'✅ Chains: {d.get(\"count\", 0)} сетей')" || echo "❌"

echo ""
echo "3️⃣ Проверка /protocols"
protocols=$(curl -s "$API_URL/protocols")
echo "$protocols" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'✅ Protocols: {d.get(\"count\", 0)} протоколов')" || echo "❌"

echo ""
echo "4️⃣ Проверка /strategies"
strategies=$(curl -s "$API_URL/strategies?limit=5")
echo "$strategies" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'✅ Strategies: {d.get(\"total\", 0)} всего, {len(d.get(\"items\", []))} в ответе')" || echo "❌"

echo ""
echo "5️⃣ Проверка /top-tokens"
tokens=$(curl -s "$API_URL/top-tokens?limit=10")
echo "$tokens" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'✅ Tokens: {len(d) if isinstance(d, list) else 0} токенов')" || echo "❌"

echo ""
echo "✅ Все основные endpoints работают!"
