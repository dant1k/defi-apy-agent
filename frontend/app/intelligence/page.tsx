'use client';

import { useState, useEffect } from 'react';
import { fetchAggregatorStrategies } from '../../lib/api';
import type { AggregatedStrategy } from '../../components/home/types';
import { AIScoring } from '../../components/ai/ai-scoring';
import { AIAlerts } from '../../components/ai/ai-alerts';
import { AISuggestions } from '../../components/ai/ai-suggestions';
import { StrategyExplainer } from '../../components/ai/strategy-explainer';

export default function IntelligencePage() {
  const [strategies, setStrategies] = useState<AggregatedStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStrategy, setSelectedStrategy] = useState<AggregatedStrategy | null>(null);
  const [showExplainer, setShowExplainer] = useState(false);

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || 
                      process.env.NEXT_PUBLIC_API_URL || 
                      'http://localhost:8000';
        
        const response = await fetch(`${apiUrl}/strategies?limit=50&sort=ai_score_desc`);
        if (response.ok) {
          const data = await response.json();
          setStrategies(data.items || []);
          if (data.items && data.items.length > 0) {
            setSelectedStrategy(data.items[0]);
          }
        }
      } catch (error) {
        console.error('Failed to load strategies:', error);
        setStrategies([]);
      } finally {
        setLoading(false);
      }
    };

    loadStrategies();
  }, []);

  const topStrategies = strategies.slice(0, 10);

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        <div className="text-center mb-12">
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-4">
            AI Intelligence
          </h1>
          <p className="font-inter text-white/80 text-lg">
            AI-powered insights, scoring, and recommendations for DeFi strategies
          </p>
        </div>

        {loading ? (
          <div className="text-center text-white/70 py-20">
            <p>Loading AI analysis...</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* AI Suggestions */}
            <div className="lg:col-span-2">
              <div className="card-genora">
                <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
                  AI-Powered Suggestions
                </h2>
                <AISuggestions strategies={topStrategies} />
              </div>
            </div>

            {/* AI Alerts */}
            <div>
              <div className="card-genora">
                <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
                  AI Alerts
                </h2>
                <AIAlerts strategies={strategies} />
              </div>
            </div>

            {/* Top Strategies with AI Scoring */}
            <div className="lg:col-span-3">
              <div className="card-genora">
                <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
                  Top Strategies with AI Analysis
                </h2>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {topStrategies.map((strategy) => (
                    <div
                      key={strategy.id}
                      className="border border-white/10 rounded-lg p-4 hover:border-[var(--neonAqua)]/50 transition-colors cursor-pointer"
                      onClick={() => {
                        setSelectedStrategy(strategy);
                        setShowExplainer(true);
                      }}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-white text-sm truncate">
                          {strategy.name}
                        </h3>
                        <span className="text-xs text-white/60 bg-white/10 px-2 py-1 rounded">
                          {strategy.chain}
                        </span>
                      </div>
                      <div className="mb-3">
                        <AIScoring strategy={strategy} />
                      </div>
                      <div className="flex justify-between text-xs text-white/70">
                        <span>APY: {(strategy.apy || 0).toFixed(2)}%</span>
                        <span>TVL: ${((strategy.tvl_usd || 0) / 1e6).toFixed(1)}M</span>
                      </div>
                      <button
                        className="mt-2 w-full text-xs text-[var(--neonAqua)] hover:underline"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedStrategy(strategy);
                          setShowExplainer(true);
                        }}
                      >
                        Explain Strategy →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Strategy Explainer Modal */}
        {showExplainer && selectedStrategy && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="card-genora max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)]">
                  Strategy Explanation
                </h2>
                <button
                  onClick={() => setShowExplainer(false)}
                  className="text-white/70 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <StrategyExplainer strategy={selectedStrategy} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

