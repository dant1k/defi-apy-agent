# 🧠 Genora Intelligence Dashboard

## Обзор

Genora Intelligence Dashboard - это продвинутый AI-дашборд с интерактивными анимациями и реальными данными из DeFi рынка. Дашборд объединяет визуальные эффекты, звуковые интеракции и AI-анализ для создания уникального пользовательского опыта.

## 🎯 Основные возможности

### 🎨 Визуальные эффекты
- **3D Parallax Grid** - интерактивная сетка, реагирующая на движение мыши
- **Plasma Streams** - анимированные потоки энергии
- **Glow Pulse** - пульсирующие световые эффекты
- **Neural Background** - фоновые нейронные паттерны

### 🔊 Звуковые интеракции
- **Mystic Pulse** - фоновый звук при загрузке
- **Hover Resonance** - звуковые эффекты при наведении
- **Audio Context** - генерация звуков в реальном времени

### 📊 Реальные данные
- **22,912 стратегий** из DeFiLlama, Beefy, Yearn, CoinGecko
- **$206B TVL** общий объем заблокированных средств
- **AI-анализ** каждой стратегии с оценками и комментариями
- **Market Insights** - рыночные инсайты и тренды

## 🚀 Компоненты

### 1. AI Feed
- **AI Insights** - автоматически генерируемые инсайты
- **Strategy Alerts** - уведомления о топ стратегиях
- **Real-time Updates** - обновления каждые 2 минуты

### 2. Strategy Performance Map
- **Интерактивные графики** (Line, Area, Bar)
- **Реальные данные** APY, TVL, Risk
- **Переключение типов** графиков в реальном времени

### 3. Market Overview
- **Топ сети** с TVL и количеством стратегий
- **Общая статистика** рынка
- **Анимированные метрики**

### 4. AI Portfolio
- **AI-рекомендованные стратегии**
- **Risk Assessment** с цветовой индикацией
- **Performance Metrics** для каждой стратегии

### 5. Comparison Lab
- **Side-by-side сравнение** стратегий
- **Multi-metric анализ** (APY, Risk, TVL, AI Score)
- **Visual indicators** для быстрого сравнения

### 6. AI Indices
- **GYI (Genora Yield Index)** - средний APY
- **AMI (AI Momentum Index)** - рост TVL
- **RAY (Risk-Adjusted Yield)** - оптимальная доходность

## 🛠 Технические детали

### Зависимости
```json
{
  "framer-motion": "^11.0.0",
  "recharts": "^2.8.0",
  "lucide-react": "^0.400.0"
}
```

### API Endpoints
- `GET /strategies` - получение стратегий
- `GET /mcp/market-insights` - рыночные инсайты
- `GET /mcp/analyze-strategy/{id}` - анализ стратегии
- `POST /mcp/compare-strategies` - сравнение стратегий

### Анимации
- **Framer Motion** для всех анимаций
- **CSS Transforms** для 3D эффектов
- **Web Audio API** для звуковых эффектов
- **Responsive Design** для всех устройств

## 📱 Использование

### Доступ к дашборду
```
http://localhost:3000/intelligence
```

### Навигация
- **Analytics Dashboard** (`/`) - основной дашборд
- **Strategies** (`/strategies`) - список стратегий
- **AI Intelligence** (`/intelligence`) - новый AI дашборд

### Интерактивность
- **Hover effects** на всех элементах
- **Click interactions** для переключения графиков
- **Mouse tracking** для 3D эффектов
- **Sound feedback** при взаимодействии

## 🎨 Стилизация

### Цветовая схема
- **Primary**: Cyan (#22d3ee) - основной цвет
- **Secondary**: Fuchsia (#d946ef) - акцентный цвет
- **Background**: Black (#000000) - фон
- **Text**: White (#ffffff) - текст

### Градиенты
- **Cyan to Fuchsia** - основные градиенты
- **Radial gradients** - фоновые эффекты
- **Linear gradients** - карточки и кнопки

### Анимации
- **Duration**: 2-30 секунд
- **Easing**: easeInOut, linear
- **Repeat**: Infinite для фоновых эффектов
- **Delay**: Staggered для последовательных анимаций

## 🔧 Настройка

### Переменные окружения
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Конфигурация анимаций
```typescript
const glowPulse = {
  initial: { opacity: 0.6, scale: 1 },
  animate: { opacity: [0.6, 1, 0.6], scale: [1, 1.05, 1] },
  transition: { duration: 3, repeat: Infinity }
};
```

## 📈 Производительность

### Оптимизации
- **Lazy loading** компонентов
- **Memoization** для тяжелых вычислений
- **Debounced** API calls
- **Efficient re-renders** с React.memo

### Мониторинг
- **Console logging** для отладки
- **Error boundaries** для обработки ошибок
- **Loading states** для UX
- **Fallback data** при недоступности API

## 🚀 Развертывание

### Локальная разработка
```bash
cd frontend
npm install
npm run dev
```

### Production build
```bash
npm run build
npm start
```

### Docker
```bash
docker-compose up -d
```

## 🎯 Roadmap

### Планируемые функции
- [ ] **Real-time WebSocket** подключения
- [ ] **Advanced AI predictions** с ML моделями
- [ ] **Portfolio tracking** для пользователей
- [ ] **Custom alerts** и уведомления
- [ ] **Export functionality** для данных
- [ ] **Mobile optimization** для мобильных устройств

### Интеграции
- [ ] **Telegram Bot** для уведомлений
- [ ] **Discord Bot** для сообщества
- [ ] **Email alerts** для важных событий
- [ ] **API webhooks** для внешних систем

## 🤝 Вклад в проект

### Как добавить новые анимации
1. Создайте новый motion объект
2. Примените к компоненту
3. Настройте timing и easing
4. Протестируйте производительность

### Как добавить новые данные
1. Обновите API endpoint
2. Добавьте типы TypeScript
3. Интегрируйте в компонент
4. Добавьте обработку ошибок

## 📞 Поддержка

Для вопросов и предложений:
- **GitHub Issues** - баги и feature requests
- **Discord** - сообщество и обсуждения
- **Email** - техническая поддержка

---

**Genora Intelligence Dashboard** - будущее DeFi аналитики с AI и интерактивными визуализациями! 🚀

