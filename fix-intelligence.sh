#!/bin/bash
# Скрипт для исправления intelligence/page.tsx на сервере
# Выполни на сервере: bash <(curl -s https://raw.githubusercontent.com/dant1k/defi-apy-agent/feature/dashboard-redesign/fix-intelligence.sh)

SERVER_IP="46.224.99.147"
FILE_PATH="/opt/defi-apy-agent/frontend/app/intelligence/page.tsx"

echo "🔧 Исправление intelligence/page.tsx на сервере..."

ssh root@${SERVER_IP} << 'ENDSSH'
cd /opt/defi-apy-agent

# Создаем бэкап
cp frontend/app/intelligence/page.tsx frontend/app/intelligence/page.tsx.bak

# Исправляем файл
cat > /tmp/fix_intelligence.txt << 'FIX'
        {/* Strategy Explainer Modal */}
        {selectedStrategy && (
          <StrategyExplainer 
            strategy={selectedStrategy} 
            isOpen={showExplainer}
            onClose={() => setShowExplainer(false)}
          />
        )}
FIX

# Находим и заменяем проблемный блок
sed -i '/Strategy Explainer Modal/,/^        )}/c\
        {/* Strategy Explainer Modal */}\
        {selectedStrategy && (\
          <StrategyExplainer \
            strategy={selectedStrategy} \
            isOpen={showExplainer}\
            onClose={() => setShowExplainer(false)}\
          />\
        )}' frontend/app/intelligence/page.tsx

echo "✅ Файл исправлен"
ENDSSH

echo "✅ Готово! Теперь пересобери:"
echo "   docker compose -f docker-compose.prod.yml up -d --build frontend"

