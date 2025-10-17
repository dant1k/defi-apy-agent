'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

interface ChartData {
  name: string;
  value: number;
  color: string;
}

interface SimpleChartsProps {
  strategies: any[];
}

export function SimpleCharts({ strategies }: SimpleChartsProps) {
  const [selectedChart, setSelectedChart] = useState<'apy' | 'tvl' | 'risk'>('apy');

  // Prepare chart data
  const apyData: ChartData[] = strategies.slice(0, 8).map((strategy, index) => ({
    name: strategy.protocol.substring(0, 8),
    value: strategy.apy,
    color: `hsl(${120 + index * 30}, 70%, 50%)`
  }));

  const tvlData: ChartData[] = strategies.slice(0, 8).map((strategy, index) => ({
    name: strategy.protocol.substring(0, 8),
    value: strategy.tvl_usd / 1000000, // Convert to millions
    color: `hsl(${200 + index * 30}, 70%, 50%)`
  }));

  const riskData: ChartData[] = strategies.slice(0, 8).map((strategy, index) => ({
    name: strategy.protocol.substring(0, 8),
    value: strategy.risk_index,
    color: `hsl(${300 + index * 30}, 70%, 50%)`
  }));

  const currentData = selectedChart === 'apy' ? apyData : selectedChart === 'tvl' ? tvlData : riskData;
  const maxValue = Math.max(...currentData.map(d => d.value));
  const unit = selectedChart === 'apy' ? '%' : selectedChart === 'tvl' ? 'M' : '';

  return (
    <motion.div 
      className="bg-gradient-to-b from-black/70 to-black/40 border border-cyan-900/50 rounded-lg p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 1.0 }}
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-cyan-400">Interactive Analytics</h2>
        <div className="flex space-x-2">
          {(['apy', 'tvl', 'risk'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setSelectedChart(type)}
              className={`px-4 py-2 rounded text-sm font-medium transition-all ${
                selectedChart === type
                  ? 'bg-cyan-600 text-white shadow-lg'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {currentData.map((item, index) => (
          <motion.div
            key={item.name}
            className="flex items-center space-x-4"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 + index * 0.1 }}
          >
            <div className="w-20 text-sm text-white/70 truncate">
              {item.name}
            </div>
            <div className="flex-1 relative">
              <div className="h-6 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.value / maxValue) * 100}%` }}
                  transition={{ delay: 1.4 + index * 0.1, duration: 0.8, ease: "easeOut" }}
                />
              </div>
            </div>
            <div className="w-16 text-sm text-white font-mono text-right">
              {item.value.toFixed(1)}{unit}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4 text-center">
        <motion.div
          className="p-4 bg-gray-800/50 rounded-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="text-2xl font-bold text-cyan-400">
            {apyData.reduce((sum, d) => sum + d.value, 0) / apyData.length}
          </div>
          <div className="text-sm text-white/60">Avg APY</div>
        </motion.div>
        <motion.div
          className="p-4 bg-gray-800/50 rounded-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="text-2xl font-bold text-fuchsia-400">
            {tvlData.reduce((sum, d) => sum + d.value, 0).toFixed(0)}M
          </div>
          <div className="text-sm text-white/60">Total TVL</div>
        </motion.div>
        <motion.div
          className="p-4 bg-gray-800/50 rounded-lg"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="text-2xl font-bold text-yellow-400">
            {riskData.reduce((sum, d) => sum + d.value, 0) / riskData.length}
          </div>
          <div className="text-sm text-white/60">Avg Risk</div>
        </motion.div>
      </div>
    </motion.div>
  );
}
