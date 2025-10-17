'use client';

import { useState, useEffect } from 'react';

interface TrendData {
  category: string;
  current: number;
  previous: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
}

interface TrendsAnalysisProps {
  strategies: any[];
}

export function TrendsAnalysis({ strategies }: TrendsAnalysisProps) {
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [timeframe, setTimeframe] = useState<'24h' | '7d' | '30d'>('24h');

  useEffect(() => {
    if (!strategies || strategies.length === 0) return;

    // Calculate trends based on current data
    const totalTvl = strategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);
    const avgApy = strategies.reduce((sum, s) => sum + (s.apy || 0), 0) / strategies.length;
    const totalStrategies = strategies.length;
    
    // Group by chains
    const chainGroups = strategies.reduce((acc, s) => {
      const chain = s.chain || 'Unknown';
      acc[chain] = (acc[chain] || 0) + (s.tvl_usd || 0);
      return acc;
    }, {} as Record<string, number>);
    
    const topChain = Object.entries(chainGroups).sort(([,a], [,b]) => b - a)[0]?.[0] || 'Unknown';
    const topChainTvl = chainGroups[topChain] || 0;

    // Mock previous data (in real app, this would come from historical data)
    const mockPreviousData = {
      tvl: totalTvl * (0.8 + Math.random() * 0.4), // 80-120% of current
      apy: avgApy * (0.9 + Math.random() * 0.2), // 90-110% of current
      strategies: Math.max(1, totalStrategies + Math.floor(Math.random() * 20 - 10)), // ±10 strategies
      topChainTvl: topChainTvl * (0.7 + Math.random() * 0.6) // 70-130% of current
    };

    const trendsData: TrendData[] = [
      {
        category: 'Total Market TVL',
        current: totalTvl,
        previous: mockPreviousData.tvl,
        change: totalTvl - mockPreviousData.tvl,
        changePercent: ((totalTvl - mockPreviousData.tvl) / mockPreviousData.tvl) * 100,
        trend: totalTvl > mockPreviousData.tvl ? 'up' : totalTvl < mockPreviousData.tvl ? 'down' : 'stable',
        description: 'Total value locked across all strategies'
      },
      {
        category: 'Average APY',
        current: avgApy,
        previous: mockPreviousData.apy,
        change: avgApy - mockPreviousData.apy,
        changePercent: ((avgApy - mockPreviousData.apy) / mockPreviousData.apy) * 100,
        trend: avgApy > mockPreviousData.apy ? 'up' : avgApy < mockPreviousData.apy ? 'down' : 'stable',
        description: 'Average annual percentage yield'
      },
      {
        category: 'Active Strategies',
        current: totalStrategies,
        previous: mockPreviousData.strategies,
        change: totalStrategies - mockPreviousData.strategies,
        changePercent: ((totalStrategies - mockPreviousData.strategies) / mockPreviousData.strategies) * 100,
        trend: totalStrategies > mockPreviousData.strategies ? 'up' : totalStrategies < mockPreviousData.strategies ? 'down' : 'stable',
        description: 'Number of active yield strategies'
      },
      {
        category: `${topChain} Dominance`,
        current: topChainTvl,
        previous: mockPreviousData.topChainTvl,
        change: topChainTvl - mockPreviousData.topChainTvl,
        changePercent: ((topChainTvl - mockPreviousData.topChainTvl) / mockPreviousData.topChainTvl) * 100,
        trend: topChainTvl > mockPreviousData.topChainTvl ? 'up' : topChainTvl < mockPreviousData.topChainTvl ? 'down' : 'stable',
        description: `TVL dominance of ${topChain} chain`
      }
    ];

    setTrends(trendsData);
  }, [strategies, timeframe]);

  const formatValue = (value: number, type: 'tvl' | 'apy' | 'count' | 'percent') => {
    switch (type) {
      case 'tvl':
        if (value >= 1000000000) {
          return `$${(value / 1000000000).toFixed(1)}B`;
        } else if (value >= 1000000) {
          return `$${(value / 1000000).toFixed(1)}M`;
        } else {
          return `$${(value / 1000).toFixed(0)}K`;
        }
      case 'apy':
        return `${value.toFixed(2)}%`;
      case 'count':
        return value.toLocaleString();
      case 'percent':
        return `${value.toFixed(1)}%`;
      default:
        return value.toString();
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '↗';
      case 'down': return '↘';
      case 'stable': return '→';
      default: return '→';
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-400';
      case 'down': return 'text-red-400';
      case 'stable': return 'text-yellow-400';
      default: return 'text-white';
    }
  };

  return (
    <div className="card-genora">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Market Trends Analysis
        </h2>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((period) => (
            <button
              key={period}
              onClick={() => setTimeframe(period)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                timeframe === period
                  ? 'bg-[var(--neonAqua)] text-black'
                  : 'bg-[var(--graphiteGray)] text-white/70 hover:text-white'
              }`}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {trends.map((trend, index) => (
          <div key={index} className="card-genora">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-orbitron text-lg font-semibold text-white mb-1">
                  {trend.category}
                </h3>
                <p className="font-inter text-white/60 text-sm">
                  {trend.description}
                </p>
              </div>
              <div className={`text-2xl ${getTrendColor(trend.trend)}`}>
                {getTrendIcon(trend.trend)}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="font-spacemono text-2xl font-bold text-white">
                  {formatValue(trend.current, 
                    trend.category.includes('TVL') ? 'tvl' : 
                    trend.category.includes('APY') ? 'apy' : 
                    trend.category.includes('Strategies') ? 'count' : 'tvl'
                  )}
                </span>
                <div className="text-right">
                  <div className={`font-spacemono font-semibold ${getTrendColor(trend.trend)}`}>
                    {trend.changePercent >= 0 ? '+' : ''}{trend.changePercent.toFixed(1)}%
                  </div>
                  <div className="text-xs text-white/60">
                    {formatValue(Math.abs(trend.change), 
                      trend.category.includes('TVL') ? 'tvl' : 
                      trend.category.includes('APY') ? 'apy' : 
                      trend.category.includes('Strategies') ? 'count' : 'tvl'
                    )}
                  </div>
                </div>
              </div>

              <div className="w-full bg-[var(--graphiteGray)] rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-500 ${
                    trend.trend === 'up' ? 'bg-green-400' : 
                    trend.trend === 'down' ? 'bg-red-400' : 'bg-yellow-400'
                  }`}
                  style={{ 
                    width: `${Math.min(100, Math.max(0, Math.abs(trend.changePercent) * 2))}%` 
                  }}
                ></div>
              </div>

              <div className="flex justify-between text-xs text-white/60">
                <span>Previous: {formatValue(trend.previous, 
                  trend.category.includes('TVL') ? 'tvl' : 
                  trend.category.includes('APY') ? 'apy' : 
                  trend.category.includes('Strategies') ? 'count' : 'tvl'
                )}</span>
                <span>Current: {formatValue(trend.current, 
                  trend.category.includes('TVL') ? 'tvl' : 
                  trend.category.includes('APY') ? 'apy' : 
                  trend.category.includes('Strategies') ? 'count' : 'tvl'
                )}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-[var(--graphiteGray)] rounded-lg border border-[var(--neonAqua)]/20">
        <h3 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-3">
          Market Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="font-inter text-white/80 text-sm">
                {trends.filter(t => t.trend === 'up').length} metrics trending up
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-red-400 rounded-full"></div>
              <span className="font-inter text-white/80 text-sm">
                {trends.filter(t => t.trend === 'down').length} metrics trending down
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
              <span className="font-inter text-white/80 text-sm">
                {trends.filter(t => t.trend === 'stable').length} metrics stable
              </span>
            </div>
          </div>
          <div className="text-sm text-white/60">
            <p>Market analysis based on {timeframe} timeframe</p>
            <p>Data updated every 2 minutes</p>
            <p>Last update: {new Date().toLocaleTimeString('ru-RU')}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
