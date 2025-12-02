'use client';

import { useState, useMemo } from 'react';
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

interface StrategySearchProps {
  strategies: Strategy[];
  onStrategySelect?: (strategy: Strategy) => void;
}

export function StrategySearch({ strategies, onStrategySelect }: StrategySearchProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const filteredStrategies = useMemo(() => {
    if (!searchTerm.trim()) return [];
    
    const term = searchTerm.toLowerCase();
    return strategies.filter(strategy => 
      strategy.protocol.toLowerCase().includes(term) ||
      strategy.chain.toLowerCase().includes(term) ||
      strategy.token_pair.toLowerCase().includes(term) ||
      strategy.name.toLowerCase().includes(term)
    ).slice(0, 8); // Limit to 8 results
  }, [strategies, searchTerm]);

  const handleStrategyClick = (strategy: Strategy) => {
    onStrategySelect?.(strategy);
    setSearchTerm('');
    setIsOpen(false);
  };

  return (
    <motion.div 
      className="relative mb-8"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
    >
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          placeholder="Search strategies, protocols, chains..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(e.target.value.length > 0);
          }}
          onFocus={() => setIsOpen(searchTerm.length > 0)}
          onBlur={() => setTimeout(() => setIsOpen(false), 200)}
          className="w-full pl-10 pr-4 py-3 bg-black/40 border border-cyan-900/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-colors"
        />
      </div>

      <AnimatePresence>
        {isOpen && filteredStrategies.length > 0 && (
          <motion.div
            className="absolute top-full left-0 right-0 mt-2 bg-black/90 border border-cyan-900/50 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto"
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            {filteredStrategies.map((strategy, index) => (
              <motion.div
                key={strategy.id}
                className="p-4 border-b border-gray-800/50 last:border-b-0 hover:bg-cyan-500/10 cursor-pointer transition-colors"
                onClick={() => handleStrategyClick(strategy)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ x: 5 }}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="text-white font-semibold">{strategy.protocol}</div>
                    <div className="text-sm text-gray-400">
                      {strategy.token_pair} • {strategy.chain}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-cyan-400 font-bold">{strategy.apy.toFixed(2)}%</div>
                    <div className="text-xs text-gray-500">
                      Risk: {strategy.risk_index.toFixed(1)}
                    </div>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  TVL: ${(strategy.tvl_usd / 1000000).toFixed(1)}M • AI Score: {strategy.ai_score.toFixed(0)}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {isOpen && searchTerm.length > 0 && filteredStrategies.length === 0 && (
        <motion.div
          className="absolute top-full left-0 right-0 mt-2 bg-black/90 border border-cyan-900/50 rounded-lg shadow-xl z-50 p-4"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <div className="text-gray-400 text-center">
            No strategies found for "{searchTerm}"
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

