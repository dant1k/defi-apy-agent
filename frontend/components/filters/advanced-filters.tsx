'use client';

import { useState } from 'react';

interface AdvancedFiltersProps {
  onFiltersChange: (filters: any) => void;
}

export function AdvancedFilters({ onFiltersChange }: AdvancedFiltersProps) {
  const [filters, setFilters] = useState({
    period: '24h',
    strategyType: 'all',
    riskLevel: 'all',
    assetType: 'all',
    trending: false,
    newPools: false,
  });

  const handleFilterChange = (key: string, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  return (
    <div className="card-genora mb-8">
      <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-6">
        Advanced Filters
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div>
          <h3 className="font-orbitron text-sm font-semibold text-white mb-3">Период данных</h3>
          <div className="space-y-2">
            {['24h', '7d', '30d'].map(period => (
              <button
                key={period}
                className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filters.period === period 
                    ? 'bg-[var(--neonAqua)] text-black' 
                    : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
                }`}
                onClick={() => handleFilterChange('period', period)}
              >
                {period}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-orbitron text-sm font-semibold text-white mb-3">Тип стратегии</h3>
          <div className="space-y-2">
            {['all', 'Lending', 'LP', 'Vaults', 'Staking', 'Real Yield', 'AI Vaults'].map(type => (
              <button
                key={type}
                className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filters.strategyType === type 
                    ? 'bg-[var(--neonAqua)] text-black' 
                    : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
                }`}
                onClick={() => handleFilterChange('strategyType', type)}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-orbitron text-sm font-semibold text-white mb-3">Риск-уровень</h3>
          <div className="space-y-2">
            {['all', 'Low', 'Medium', 'High'].map(risk => (
              <button
                key={risk}
                className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filters.riskLevel === risk 
                    ? 'bg-[var(--neonAqua)] text-black' 
                    : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
                }`}
                onClick={() => handleFilterChange('riskLevel', risk)}
              >
                {risk}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-orbitron text-sm font-semibold text-white mb-3">Тип активов</h3>
          <div className="space-y-2">
            {['all', 'Stable', 'Volatile'].map(type => (
              <button
                key={type}
                className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                  filters.assetType === type 
                    ? 'bg-[var(--neonAqua)] text-black' 
                    : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
                }`}
                onClick={() => handleFilterChange('assetType', type)}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-orbitron text-sm font-semibold text-white mb-3">Тренды</h3>
          <div className="space-y-3">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.trending}
                onChange={(e) => handleFilterChange('trending', e.target.checked)}
                className="w-4 h-4 text-[var(--neonAqua)] bg-[var(--graphiteGray)] border-gray-600 rounded focus:ring-[var(--neonAqua)]"
              />
              <span className="font-inter text-sm text-white/70">Trending</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.newPools}
                onChange={(e) => handleFilterChange('newPools', e.target.checked)}
                className="w-4 h-4 text-[var(--neonAqua)] bg-[var(--graphiteGray)] border-gray-600 rounded focus:ring-[var(--neonAqua)]"
              />
              <span className="font-inter text-sm text-white/70">New Pools</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
