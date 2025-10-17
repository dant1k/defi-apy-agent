'use client';

import { useState, useEffect } from 'react';
import { fetchAggregatorStrategies } from '../../lib/api';
import type { AggregatedStrategy } from '../../components/home/types';
import { StrategyChart } from '../../components/charts/strategy-chart';
import { RiskMatrix } from '../../components/charts/risk-matrix';
import { AIScoring } from '../../components/ai/ai-scoring';
import { AIAlerts } from '../../components/ai/ai-alerts';
import { StrategyExplainer } from '../../components/ai/strategy-explainer';
import { Watchlist } from '../../components/interactive/watchlist';
import { WalletConnector } from '../../components/interactive/wallet-connector';
import { GlobalSearch } from '../../components/search/global-search';
import { MarketOverview } from '../../components/market/market-overview';
import './dashboard.css';

// Remove old MarketOverview component - using the new one from components/market

// Advanced Filters Component
function AdvancedFilters({ onFiltersChange }: { onFiltersChange: (filters: any) => void }) {
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
    <div className="advanced-filters">
      <div className="filter-section">
        <h3>Период данных</h3>
        <div className="filter-options">
          {['24h', '7d', '30d'].map(period => (
            <button
              key={period}
              className={`filter-btn ${filters.period === period ? 'active' : ''}`}
              onClick={() => handleFilterChange('period', period)}
            >
              {period}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <h3>Тип стратегии</h3>
        <div className="filter-options">
          {['all', 'Lending', 'LP', 'Vaults', 'Staking', 'Real Yield', 'AI Vaults'].map(type => (
            <button
              key={type}
              className={`filter-btn ${filters.strategyType === type ? 'active' : ''}`}
              onClick={() => handleFilterChange('strategyType', type)}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <h3>Риск-уровень</h3>
        <div className="filter-options">
          {['all', 'Low', 'Medium', 'High'].map(risk => (
            <button
              key={risk}
              className={`filter-btn risk-${risk.toLowerCase()} ${filters.riskLevel === risk ? 'active' : ''}`}
              onClick={() => handleFilterChange('riskLevel', risk)}
            >
              {risk}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <h3>Тип активов</h3>
        <div className="filter-options">
          {['all', 'Stable', 'Volatile'].map(type => (
            <button
              key={type}
              className={`filter-btn ${filters.assetType === type ? 'active' : ''}`}
              onClick={() => handleFilterChange('assetType', type)}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-section">
        <h3>Тренды</h3>
        <div className="filter-options">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.trending}
              onChange={(e) => handleFilterChange('trending', e.target.checked)}
            />
            Trending
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.newPools}
              onChange={(e) => handleFilterChange('newPools', e.target.checked)}
            />
            New Pools
          </label>
        </div>
      </div>
    </div>
  );
}

// AI Suggestions Component
function AISuggestions() {
  const suggestions = [
    {
      id: 1,
      name: "Aave V3 USDC",
      apy: 8.5,
      risk: "Low",
      reason: "High TVL stability with consistent yield",
      chain: "Ethereum",
      icon: "🏛️"
    },
    {
      id: 2,
      name: "Uniswap V3 ETH/USDC",
      apy: 12.3,
      risk: "Medium",
      reason: "Optimal liquidity range with growing volume",
      chain: "Ethereum",
      icon: "🔄"
    },
    {
      id: 3,
      name: "Compound USDT",
      apy: 6.8,
      risk: "Low",
      reason: "Stable lending protocol with proven track record",
      chain: "Ethereum",
      icon: "💰"
    }
  ];

  return (
    <div className="ai-suggestions">
      <h2>AI Smart Suggestions</h2>
      <div className="suggestions-grid">
        {suggestions.map(suggestion => (
          <div key={suggestion.id} className="suggestion-card">
            <div className="suggestion-header">
              <div className="suggestion-title">
                <span className="suggestion-icon">{suggestion.icon}</span>
                <h4>{suggestion.name}</h4>
              </div>
              <span className={`risk-badge risk-${suggestion.risk.toLowerCase()}`}>
                {suggestion.risk}
              </span>
            </div>
            <div className="suggestion-apy">{suggestion.apy}% APY</div>
            <div className="suggestion-reason">{suggestion.reason}</div>
            <div className="suggestion-chain">{suggestion.chain}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Main Dashboard Component
export default function DashboardClient() {
  const [strategies, setStrategies] = useState<AggregatedStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);
  const [showExplainer, setShowExplainer] = useState(false);

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        setLoading(true);
        const response = await fetchAggregatorStrategies(
          process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
          {
            chain: null,
            protocol: null,
            min_tvl: null,
            min_apy: null,
            sort: 'ai_score_desc',
            limit: 50,
          }
        );
        setStrategies(response.items);
      } catch (error) {
        console.error('Failed to load strategies:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStrategies();
  }, []);

  const handleFiltersChange = (newFilters: any) => {
    setFilters(newFilters);
    // TODO: Apply filters to strategies
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>DeFi Analytics Dashboard</h1>
        <p>AI-powered insights for optimal yield strategies</p>
      </div>

      <GlobalSearch 
        strategies={strategies}
        onResultClick={(result) => {
          console.log('Search result clicked:', result);
          // TODO: Navigate to result or show details
        }}
      />

      <MarketOverview strategies={strategies} />

      <div className="dashboard-content">
        <div className="dashboard-sidebar">
          <WalletConnector />
          <Watchlist strategies={strategies} />
          <AdvancedFilters onFiltersChange={handleFiltersChange} />
        </div>

        <div className="dashboard-main">
          <AISuggestions />
          
          {/* AI Alerts */}
          <AIAlerts strategies={strategies} />
          
          {/* Strategy Chart */}
          {strategies.length > 0 && (
            <StrategyChart 
              strategyId={strategies[0].id} 
              strategyName={strategies[0].name}
              type="both"
            />
          )}
          
          {/* Risk Matrix */}
          {strategies.length > 0 && (
            <RiskMatrix strategies={strategies} />
          )}
          
          {/* AI Scoring for top strategy */}
          {strategies.length > 0 && (
            <AIScoring strategy={strategies[0]} />
          )}
          
          <div className="strategies-section">
            <h2>Top Strategies</h2>
            {loading ? (
              <div className="loading">Loading strategies...</div>
            ) : (
              <div className="strategies-grid">
                {strategies.slice(0, 12).map(strategy => (
                  <div 
                    key={strategy.id} 
                    className="strategy-card"
                    onClick={() => {
                      setSelectedStrategy(strategy);
                      setShowExplainer(true);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="strategy-header">
                      <h4>{strategy.name}</h4>
                      <span className="strategy-chain">{strategy.chain}</span>
                    </div>
                    <div className="strategy-metrics">
                      <div className="metric">
                        <span className="metric-label">APY</span>
                        <span className="metric-value">{strategy.apy.toFixed(2)}%</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">TVL</span>
                        <span className="metric-value">${(strategy.tvl_usd / 1000000).toFixed(1)}M</span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">AI Score</span>
                        <span className="metric-value">{strategy.ai_score?.toFixed(1) || 'N/A'}</span>
                      </div>
                    </div>
                    <div className="strategy-protocol">{strategy.protocol}</div>
                    <div className="strategy-actions">
                      <button className="explain-btn">Explain</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Strategy Explainer Modal */}
      {selectedStrategy && (
        <StrategyExplainer
          strategy={selectedStrategy}
          isOpen={showExplainer}
          onClose={() => {
            setShowExplainer(false);
            setSelectedStrategy(null);
          }}
        />
      )}
    </div>
  );
}
