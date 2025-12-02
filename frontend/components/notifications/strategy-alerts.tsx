'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Strategy {
  id: string;
  name: string;
  protocol: string;
  chain: string;
  apy: number;
  tvl_usd: number;
  risk_index: number;
  ai_score: number;
  ai_comment: string;
  token_pair: string;
  tvl_growth_24h: number;
}

interface StrategyAlertsProps {
  strategies: Strategy[];
  previousStrategies?: Strategy[];
}

interface Alert {
  id: string;
  type: 'new' | 'high_apy' | 'trending' | 'risk_change';
  title: string;
  message: string;
  strategy: Strategy;
  timestamp: Date;
}

export function StrategyAlerts({ strategies, previousStrategies = [] }: StrategyAlertsProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [showAlerts, setShowAlerts] = useState(true);

  useEffect(() => {
    if (previousStrategies.length === 0) return;

    const newAlerts: Alert[] = [];

    // Check for new strategies
    const newStrategies = strategies.filter(
      strategy => !previousStrategies.some(prev => prev.id === strategy.id)
    );

    newStrategies.forEach(strategy => {
      newAlerts.push({
        id: `new-${strategy.id}`,
        type: 'new',
        title: 'New Strategy Detected',
        message: `${strategy.protocol} on ${strategy.chain} with ${strategy.apy.toFixed(2)}% APY`,
        strategy,
        timestamp: new Date()
      });
    });

    // Check for high APY strategies
    strategies
      .filter(strategy => strategy.apy > 20)
      .forEach(strategy => {
        newAlerts.push({
          id: `high-apy-${strategy.id}`,
          type: 'high_apy',
          title: 'High APY Alert',
          message: `${strategy.protocol} showing ${strategy.apy.toFixed(2)}% APY`,
          strategy,
          timestamp: new Date()
        });
      });

    // Check for trending strategies (high TVL growth)
    strategies
      .filter(strategy => strategy.tvl_growth_24h > 10)
      .forEach(strategy => {
        newAlerts.push({
          id: `trending-${strategy.id}`,
          type: 'trending',
          title: 'Trending Strategy',
          message: `${strategy.protocol} TVL up ${strategy.tvl_growth_24h.toFixed(1)}% in 24h`,
          strategy,
          timestamp: new Date()
        });
      });

    if (newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 5)); // Keep only 5 latest alerts
    }
  }, [strategies, previousStrategies]);

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'new': return '🆕';
      case 'high_apy': return '📈';
      case 'trending': return '🔥';
      case 'risk_change': return '⚠️';
      default: return '📢';
    }
  };

  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'new': return 'border-blue-500/50 bg-blue-500/10';
      case 'high_apy': return 'border-green-500/50 bg-green-500/10';
      case 'trending': return 'border-orange-500/50 bg-orange-500/10';
      case 'risk_change': return 'border-red-500/50 bg-red-500/10';
      default: return 'border-gray-500/50 bg-gray-500/10';
    }
  };

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  if (alerts.length === 0) return null;

  return (
    <motion.div 
      className="fixed top-4 right-4 z-50 space-y-2 max-w-sm"
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <AnimatePresence>
        {showAlerts && alerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            className={`p-4 rounded-lg border backdrop-blur-sm ${getAlertColor(alert.type)}`}
            initial={{ opacity: 0, x: 100, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 100, scale: 0.9 }}
            transition={{ 
              delay: index * 0.1,
              type: "spring",
              stiffness: 200
            }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">{getAlertIcon(alert.type)}</div>
                <div className="flex-1">
                  <div className="font-semibold text-white text-sm">
                    {alert.title}
                  </div>
                  <div className="text-white/80 text-xs mt-1">
                    {alert.message}
                  </div>
                  <div className="text-white/60 text-xs mt-1">
                    {alert.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
              <button
                onClick={() => dismissAlert(alert.id)}
                className="text-white/60 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {alerts.length > 0 && (
        <motion.button
          onClick={() => setShowAlerts(!showAlerts)}
          className="w-full px-3 py-2 bg-black/50 text-white/80 text-xs rounded hover:bg-black/70 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {showAlerts ? 'Hide Alerts' : `Show ${alerts.length} Alerts`}
        </motion.button>
      )}
    </motion.div>
  );
}

