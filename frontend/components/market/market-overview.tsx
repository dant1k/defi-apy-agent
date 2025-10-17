'use client';

import { useState, useEffect } from 'react';

interface MarketTrend {
  id: string;
  title: string;
  description: string;
  change: number;
  type: 'positive' | 'negative' | 'neutral';
  category: 'apy' | 'tvl' | 'protocol' | 'chain';
}

interface MarketOverviewProps {
  strategies?: any[];
}

export function MarketOverview({ strategies }: MarketOverviewProps) {
  const [marketData, setMarketData] = useState({
    totalTvl: 0,
    totalStrategies: 0,
    avgApy: 0,
    topProtocol: '',
    topChain: '',
    lastUpdate: new Date()
  });
  const [isLoading, setIsLoading] = useState(true);

  const [trends, setTrends] = useState<MarketTrend[]>([]);

  useEffect(() => {
    // Ensure strategies is an array
    const safeStrategies = strategies || [];
    
    // Calculate market data from strategies
    const totalTvl = safeStrategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);
    const totalStrategies = safeStrategies.length;
    const avgApy = safeStrategies.length > 0 
      ? safeStrategies.reduce((sum, s) => sum + (s.apy || 0), 0) / safeStrategies.length 
      : 0;

    // Find top protocol and chain by TVL
    const protocolTvl = safeStrategies.reduce((acc, s) => {
      const protocol = s.protocol || 'Unknown';
      acc[protocol] = (acc[protocol] || 0) + (s.tvl_usd || 0);
      return acc;
    }, {} as Record<string, number>);

    const chainTvl = safeStrategies.reduce((acc, s) => {
      const chain = s.chain || 'Unknown';
      acc[chain] = (acc[chain] || 0) + (s.tvl_usd || 0);
      return acc;
    }, {} as Record<string, number>);

    const topProtocol = Object.entries(protocolTvl).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';
    const topChain = Object.entries(chainTvl).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';

    setMarketData({
      totalTvl,
      totalStrategies,
      avgApy,
      topProtocol,
      topChain,
      lastUpdate: new Date()
    });

    // Generate trends
    const mockTrends: MarketTrend[] = [
      {
        id: 'ai-vaults',
        title: 'AI Vaults Surge',
        description: 'AI-powered strategies gaining 12% more APY this week',
        change: 12.5,
        type: 'positive',
        category: 'apy'
      },
      {
        id: 'ethereum-dominance',
        title: 'Ethereum TVL Growth',
        description: 'Ethereum-based strategies see 8% TVL increase',
        change: 8.2,
        type: 'positive',
        category: 'tvl'
      },
      {
        id: 'lending-protocols',
        title: 'Lending Protocols Trend',
        description: 'Aave and Compound leading yield opportunities',
        change: 5.7,
        type: 'positive',
        category: 'protocol'
      },
      {
        id: 'layer2-adoption',
        title: 'Layer 2 Expansion',
        description: 'Arbitrum and Optimism showing strong growth',
        change: 15.3,
        type: 'positive',
        category: 'chain'
      },
      {
        id: 'stable-yield',
        title: 'Stable Yield Focus',
        description: 'Investors shifting to lower-risk strategies',
        change: -3.2,
        type: 'negative',
        category: 'apy'
      }
    ];

    setTrends(mockTrends);
    setIsLoading(false);
  }, [strategies]);

  const formatTvl = (tvl: number) => {
    if (tvl >= 1000000000) {
      return `$${(tvl / 1000000000).toFixed(1)}B`;
    } else if (tvl >= 1000000) {
      return `$${(tvl / 1000000).toFixed(1)}M`;
    } else {
      return `$${(tvl / 1000).toFixed(0)}K`;
    }
  };

  const getTrendIcon = (category: string) => {
    switch (category) {
      case 'apy': return '📈';
      case 'tvl': return '💰';
      case 'protocol': return '🏛️';
      case 'chain': return '⛓️';
      default: return '📊';
    }
  };

  const getTrendColor = (type: string) => {
    switch (type) {
      case 'positive': return '#48bb78';
      case 'negative': return '#f56565';
      case 'neutral': return '#a0aec0';
      default: return '#a0aec0';
    }
  };

  return (
    <div className="card-genora mb-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)]">
          Market Overview
        </h2>
        <div className="font-spacemono text-sm text-white/60">
          Last updated: {marketData.lastUpdate.toLocaleTimeString('ru-RU')}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="stat-genora shadow-glow">
          <h3>Total Market TVL</h3>
          {isLoading ? (
            <div className="animate-pulse bg-white/20 h-8 w-24 rounded"></div>
          ) : (
            <p className="font-spacemono text-2xl font-bold">{formatTvl(marketData.totalTvl)}</p>
          )}
          <div className="text-[var(--profitGreen)] text-sm font-medium">+5.2%</div>
        </div>

        <div className="stat-genora">
          <h3>Active Strategies</h3>
          {isLoading ? (
            <div className="animate-pulse bg-white/20 h-8 w-16 rounded"></div>
          ) : (
            <p className="font-spacemono text-2xl font-bold">{marketData.totalStrategies}</p>
          )}
          <div className="text-[var(--profitGreen)] text-sm font-medium">+12 new</div>
        </div>

        <div className="stat-genora">
          <h3>Average APY</h3>
          {isLoading ? (
            <div className="animate-pulse bg-white/20 h-8 w-20 rounded"></div>
          ) : (
            <p className="font-spacemono text-2xl font-bold">{marketData.avgApy.toFixed(2)}%</p>
          )}
          <div className="text-[var(--profitGreen)] text-sm font-medium">+0.8%</div>
        </div>

        <div className="stat-genora">
          <h3>Top Protocol</h3>
          {isLoading ? (
            <div className="animate-pulse bg-white/20 h-6 w-32 rounded"></div>
          ) : (
            <p className="font-spacemono text-lg font-bold break-words">
              {marketData.topProtocol}
            </p>
          )}
          <div className="text-white/60 text-sm">Leading</div>
        </div>

        <div className="stat-genora">
          <h3>Top Chain</h3>
          {isLoading ? (
            <div className="animate-pulse bg-white/20 h-8 w-24 rounded"></div>
          ) : (
            <p className="font-spacemono text-2xl font-bold">{marketData.topChain}</p>
          )}
          <div className="text-white/60 text-sm">Dominant</div>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
          Market Trends
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {trends.map(trend => (
            <div 
              key={trend.id} 
              className="card-genora"
              style={{ borderLeftColor: getTrendColor(trend.type) }}
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-orbitron text-lg font-semibold text-white">
                  {trend.title}
                </h4>
                <span className={`font-spacemono font-bold ${
                  trend.change > 0 ? 'text-[var(--profitGreen)]' : 'text-red-400'
                }`}>
                  {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
                </span>
              </div>
              <p className="font-inter text-white/70 text-sm">{trend.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8">
        <h3 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
          AI Market Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-genora">
            <h4 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-2">
              Yield Optimization
            </h4>
            <p className="font-inter text-white/70 text-sm">
              AI algorithms are identifying 23% more profitable strategies this week compared to manual selection.
            </p>
          </div>
          <div className="card-genora">
            <h4 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-2">
              Risk Management
            </h4>
            <p className="font-inter text-white/70 text-sm">
              Smart risk scoring has prevented 15 potential losses in high-volatility strategies.
            </p>
          </div>
          <div className="card-genora">
            <h4 className="font-orbitron text-lg font-semibold text-[var(--neonAqua)] mb-2">
              Market Dynamics
            </h4>
            <p className="font-inter text-white/70 text-sm">
              Layer 2 protocols are showing 40% faster growth than mainnet alternatives.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
