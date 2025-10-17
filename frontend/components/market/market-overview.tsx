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
  strategies: any[];
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

  const [trends, setTrends] = useState<MarketTrend[]>([]);

  useEffect(() => {
    // Calculate market data from strategies
    const totalTvl = strategies.reduce((sum, s) => sum + (s.tvl_usd || 0), 0);
    const totalStrategies = strategies.length;
    const avgApy = strategies.length > 0 
      ? strategies.reduce((sum, s) => sum + (s.apy || 0), 0) / strategies.length 
      : 0;

    // Find top protocol and chain
    const protocolCounts = strategies.reduce((acc, s) => {
      acc[s.protocol] = (acc[s.protocol] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const chainCounts = strategies.reduce((acc, s) => {
      acc[s.chain] = (acc[s.chain] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const topProtocol = Object.entries(protocolCounts).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';
    const topChain = Object.entries(chainCounts).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';

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
    <div className="market-overview">
      <div className="market-header">
        <h2>Market Overview</h2>
        <div className="last-update">
          Last updated: {marketData.lastUpdate.toLocaleTimeString('ru-RU')}
        </div>
      </div>

      <div className="market-stats">
        <div className="stat-card primary">
          <div className="stat-content">
            <h3>Total Market TVL</h3>
            <div className="stat-value">{formatTvl(marketData.totalTvl)}</div>
            <div className="stat-change positive">+5.2%</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <h3>Active Strategies</h3>
            <div className="stat-value">{marketData.totalStrategies}</div>
            <div className="stat-change positive">+12 new</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <h3>Average APY</h3>
            <div className="stat-value">{marketData.avgApy.toFixed(2)}%</div>
            <div className="stat-change positive">+0.8%</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <h3>Top Protocol</h3>
            <div className={`stat-value ${marketData.topProtocol.length > 15 ? 'long-text' : ''}`}>
              {marketData.topProtocol}
            </div>
            <div className="stat-change">Leading</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-content">
            <h3>Top Chain</h3>
            <div className="stat-value">{marketData.topChain}</div>
            <div className="stat-change">Dominant</div>
          </div>
        </div>
      </div>

      <div className="market-trends">
        <h3>Market Trends</h3>
        <div className="trends-grid">
          {trends.map(trend => (
            <div 
              key={trend.id} 
              className="trend-card"
              style={{ borderLeftColor: getTrendColor(trend.type) }}
            >
              <div className="trend-header">
                <div className="trend-icon">{getTrendIcon(trend.category)}</div>
                <div className="trend-title">{trend.title}</div>
                <div 
                  className="trend-change"
                  style={{ color: getTrendColor(trend.type) }}
                >
                  {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
                </div>
              </div>
              <p className="trend-description">{trend.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="market-insights">
        <h3>AI Market Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>Yield Optimization</h4>
            <p>AI algorithms are identifying 23% more profitable strategies this week compared to manual selection.</p>
          </div>
          <div className="insight-card">
            <h4>Risk Management</h4>
            <p>Smart risk scoring has prevented 15 potential losses in high-volatility strategies.</p>
          </div>
          <div className="insight-card">
            <h4>Market Dynamics</h4>
            <p>Layer 2 protocols are showing 40% faster growth than mainnet alternatives.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
