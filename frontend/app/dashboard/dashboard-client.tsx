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
import { AdvancedFilters } from '../../components/filters/advanced-filters';
import { AISuggestions } from '../../components/ai/ai-suggestions';
import './dashboard.css';

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
    <div className="min-h-screen bg-[var(--darkVoid)] pt-20">
      <div className="container mx-auto px-6 py-8">
        <div className="text-center mb-12">
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-4">
            DeFi Analytics Dashboard
          </h1>
          <p className="font-inter text-white/80 text-lg">
            AI-powered insights for optimal yield strategies
          </p>
        </div>

        <GlobalSearch 
          strategies={strategies}
          onResultClick={(result) => {
            console.log('Search result clicked:', result);
          }}
        />

        <MarketOverview />

        <AdvancedFilters onFiltersChange={handleFiltersChange} />

        <AISuggestions strategies={strategies} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2">
            <AIAlerts strategies={strategies} />
          </div>
          <div>
            <Watchlist strategies={strategies} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <WalletConnector />
        </div>

        <div className="dashboard-main">
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
          
          <div className="card-genora">
            <h2 className="font-orbitron text-2xl font-bold text-[var(--neonAqua)] mb-6">
              Top Strategies
            </h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="font-inter text-white/60">Loading strategies...</div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {strategies.slice(0, 12).map(strategy => (
                  <div 
                    key={strategy.id} 
                    className="card-genora cursor-pointer hover:shadow-glow transition-all duration-300"
                    onClick={() => {
                      setSelectedStrategy(strategy);
                      setShowExplainer(true);
                    }}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-orbitron text-lg font-semibold text-white">
                        {strategy.name}
                      </h3>
                      <div className="font-spacemono text-xl font-bold text-[var(--profitGreen)]">
                        {strategy.apy.toFixed(2)}%
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between">
                        <span className="font-inter text-white/60 text-sm">TVL</span>
                        <span className="font-spacemono text-sm font-medium text-white">
                          ${(strategy.tvl_usd / 1000000).toFixed(1)}M
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-inter text-white/60 text-sm">Chain</span>
                        <span className="font-inter text-sm font-medium text-white">
                          {strategy.chain}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-inter text-white/60 text-sm">AI Score</span>
                        <span className="font-spacemono text-sm font-medium text-[var(--neonAqua)]">
                          {strategy.ai_score?.toFixed(1) || 'N/A'}
                        </span>
                      </div>
                    </div>
                    
                    <div className="font-inter text-white/50 text-xs mb-3">{strategy.protocol}</div>
                    
                    <button className="button-genora w-full text-sm">
                      Explain Strategy
                    </button>
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