'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SimpleCharts } from '../charts/simple-charts';
import { StrategySearch } from '../search/strategy-search';

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

// Mock data for testing
const mockStrategies: Strategy[] = [
  {
    id: "mock-1",
    name: "Aave USDC Lending",
    protocol: "aave-v3",
    chain: "Ethereum",
    apy: 8.5,
    tvl_usd: 1500000000,
    risk_index: 2.1,
    ai_score: 95,
    ai_comment: "Отличная стратегия с низким риском и стабильной доходностью",
    token_pair: "USDC-ETH",
    tvl_growth_24h: 2.3
  },
  {
    id: "mock-2",
    name: "Uniswap V3 ETH/USDC",
    protocol: "uniswap-v3",
    chain: "Ethereum",
    apy: 12.3,
    tvl_usd: 850000000,
    risk_index: 4.2,
    ai_score: 88,
    ai_comment: "Высокая доходность с умеренным риском",
    token_pair: "ETH-USDC",
    tvl_growth_24h: -1.2
  },
  {
    id: "mock-3",
    name: "Lido ETH Staking",
    protocol: "lido",
    chain: "Ethereum",
    apy: 5.4,
    tvl_usd: 3200000000,
    risk_index: 1.8,
    ai_score: 92,
    ai_comment: "Самая безопасная стратегия стейкинга ETH",
    token_pair: "ETH-ETH",
    tvl_growth_24h: 0.8
  },
  {
    id: "mock-4",
    name: "Compound USDT",
    protocol: "compound",
    chain: "Ethereum",
    apy: 6.8,
    tvl_usd: 450000000,
    risk_index: 2.5,
    ai_score: 85,
    ai_comment: "Стабильная доходность от кредитования USDT",
    token_pair: "USDT-ETH",
    tvl_growth_24h: 1.5
  },
  {
    id: "mock-5",
    name: "Curve 3Pool",
    protocol: "curve",
    chain: "Ethereum",
    apy: 4.2,
    tvl_usd: 1200000000,
    risk_index: 1.9,
    ai_score: 90,
    ai_comment: "Низкий риск, стабильная доходность от стейблкоинов",
    token_pair: "USDC-USDT-DAI",
    tvl_growth_24h: 0.3
  },
  {
    id: "mock-6",
    name: "Yearn USDC Vault",
    protocol: "yearn",
    chain: "Ethereum",
    apy: 9.1,
    tvl_usd: 320000000,
    risk_index: 3.8,
    ai_score: 82,
    ai_comment: "Автоматизированная стратегия с хорошей доходностью",
    token_pair: "USDC-ETH",
    tvl_growth_24h: -0.5
  }
];

export default function MockIntelligenceDashboard() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'testing'>('testing');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setApiStatus('testing');
        
        // Try to connect to real API
        try {
          const response = await fetch('http://localhost:8000/strategies?limit=10&sort=ai_score_desc');
          if (response.ok) {
            const data = await response.json();
            if (data.items && data.items.length > 0) {
              setStrategies(data.items);
              setApiStatus('connected');
              return;
            }
          }
        } catch (error) {
          console.log('API not available, using mock data');
        }
        
        // Use mock data if API is not available
        setStrategies(mockStrategies);
        setApiStatus('disconnected');
        
      } catch (error) {
        console.error('Error loading data:', error);
        setStrategies(mockStrategies);
        setApiStatus('disconnected');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatTvl = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else {
      return `$${(value / 1000).toFixed(0)}K`;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-pulse">🧠</div>
          <div className="text-xl text-cyan-400 mb-2">Genora Intelligence Dashboard</div>
          <div className="text-white/60">Загрузка данных...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div 
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.h1 
            className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-fuchsia-500 bg-clip-text text-transparent mb-2"
            animate={{ 
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
            }}
            transition={{ 
              duration: 3,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              backgroundSize: "200% 200%"
            }}
          >
            🧠 Genora Intelligence Dashboard
          </motion.h1>
          <motion.p 
            className="text-white/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            AI-powered DeFi analytics with real-time data
          </motion.p>
          <motion.div 
            className="mt-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.4 }}
          >
            <motion.span 
              className={`px-3 py-1 rounded-full text-sm ${
                apiStatus === 'connected' ? 'bg-green-500/20 text-green-400' :
                apiStatus === 'disconnected' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-blue-500/20 text-blue-400'
              }`}
              animate={apiStatus === 'connected' ? {
                boxShadow: [
                  "0 0 0 0 rgba(34, 197, 94, 0.4)",
                  "0 0 0 10px rgba(34, 197, 94, 0)",
                  "0 0 0 0 rgba(34, 197, 94, 0)"
                ]
              } : {}}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {apiStatus === 'connected' ? '✅ Live Data' : 
               apiStatus === 'disconnected' ? '⚠️ Demo Mode' : 
               '🔄 Testing Connection'}
            </motion.span>
          </motion.div>
        </motion.div>

        {/* Search */}
        <StrategySearch 
          strategies={strategies} 
          onStrategySelect={(strategy) => {
            console.log('Selected strategy:', strategy);
            // You can add more functionality here, like showing a modal or navigating to details
          }}
        />

        {/* Stats */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, staggerChildren: 0.1 }}
        >
          <motion.div 
            className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 hover:border-cyan-500/50 transition-colors"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-2xl font-bold text-cyan-400"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              {strategies.length}
            </motion.div>
            <div className="text-white/60">Total Strategies</div>
          </motion.div>
          <motion.div 
            className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 hover:border-fuchsia-500/50 transition-colors"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-2xl font-bold text-fuchsia-400"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
            >
              {formatTvl(strategies.reduce((sum, s) => sum + s.tvl_usd, 0))}
            </motion.div>
            <div className="text-white/60">Total TVL</div>
          </motion.div>
          <motion.div 
            className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 hover:border-green-500/50 transition-colors"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-2xl font-bold text-green-400"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
            >
              {strategies.length > 0 ? (strategies.reduce((sum, s) => sum + s.apy, 0) / strategies.length).toFixed(2) : 0}%
            </motion.div>
            <div className="text-white/60">Average APY</div>
          </motion.div>
          <motion.div 
            className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 hover:border-yellow-500/50 transition-colors"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-2xl font-bold text-yellow-400"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
            >
              {strategies.length > 0 ? (strategies.reduce((sum, s) => sum + s.ai_score, 0) / strategies.length).toFixed(0) : 0}
            </motion.div>
            <div className="text-white/60">Avg AI Score</div>
          </motion.div>
        </motion.div>

        {/* Top Strategies */}
        <motion.div 
          className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h2 className="text-2xl font-bold text-cyan-400 mb-6">Top AI-Recommended Strategies</h2>
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <AnimatePresence>
              {strategies.slice(0, 6).map((strategy, index) => (
                <motion.div 
                  key={strategy.id} 
                  className="bg-black/40 border border-fuchsia-900/50 rounded-lg p-4 hover:border-fuchsia-500/50 transition-colors"
                  initial={{ opacity: 0, y: 20, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.9 }}
                  transition={{ 
                    duration: 0.4, 
                    delay: 0.6 + index * 0.1,
                    type: "spring",
                    stiffness: 200
                  }}
                  whileHover={{ 
                    scale: 1.05,
                    y: -5,
                    transition: { duration: 0.2 }
                  }}
                  whileTap={{ scale: 0.95 }}
                >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold text-white">{strategy.protocol}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    strategy.risk_index < 3 ? 'bg-green-500/20 text-green-400' :
                    strategy.risk_index < 6 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    Risk: {strategy.risk_index.toFixed(1)}
                  </span>
                </div>
                <div className="text-2xl font-bold text-fuchsia-400 mb-2">
                  {strategy.apy.toFixed(2)}% APY
                </div>
                <div className="text-sm text-white/70 mb-2">
                  {strategy.token_pair} • {strategy.chain}
                </div>
                <div className="text-sm text-cyan-300 mb-2">
                  TVL: {formatTvl(strategy.tvl_usd)}
                </div>
                <div className="text-xs text-white/50 mb-2">
                  AI Score: {strategy.ai_score.toFixed(0)}/100
                </div>
                {strategy.tvl_growth_24h !== 0 && (
                  <div className={`text-xs ${strategy.tvl_growth_24h > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    24h TVL: {strategy.tvl_growth_24h > 0 ? '+' : ''}{strategy.tvl_growth_24h.toFixed(1)}%
                  </div>
                )}
                {strategy.ai_comment && (
                  <div className="text-xs text-white/60 mt-2 p-2 bg-black/20 rounded">
                    {strategy.ai_comment}
                  </div>
                )}
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        </motion.div>

        {/* Interactive Charts */}
        <SimpleCharts strategies={strategies} />

        {/* API Info */}
        <motion.div 
          className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <h2 className="text-xl font-bold text-cyan-400 mb-4">System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-white/60">API URL:</div>
              <div className="text-white">http://localhost:8000</div>
            </div>
            <div>
              <div className="text-white/60">Status:</div>
              <div className={apiStatus === 'connected' ? 'text-green-400' : 'text-yellow-400'}>
                {apiStatus === 'connected' ? '✅ Connected' : '⚠️ Demo Mode'}
              </div>
            </div>
            <div>
              <div className="text-white/60">Strategies Loaded:</div>
              <div className="text-white">{strategies.length}</div>
            </div>
            <div>
              <div className="text-white/60">Last Update:</div>
              <div className="text-white">{new Date().toLocaleString()}</div>
            </div>
          </div>
          {apiStatus === 'disconnected' && (
            <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
              <div className="text-yellow-200 text-sm">
                <strong>Demo Mode:</strong> Показываются демонстрационные данные. 
                Для подключения к реальному API убедитесь, что backend запущен на порту 8000.
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
