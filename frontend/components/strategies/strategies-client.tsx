'use client';

import { useEffect, useState } from "react";
import { fetchAggregatorStrategies } from "../../lib/api";
import type { AggregatedStrategy } from "../home/types";
import Link from "next/link";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

type SortBy = "ai_score_desc" | "apy_desc" | "tvl_desc" | "tvl_growth_desc";

export function StrategiesClient(): JSX.Element {
  const [strategies, setStrategies] = useState<AggregatedStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortBy>("ai_score_desc");
  const [minTvl, setMinTvl] = useState<string>("0");
  const [minApy, setMinApy] = useState<string>("0");
  const [selectedChain, setSelectedChain] = useState<string | null>(null);
  const [selectedProtocol, setSelectedProtocol] = useState<string | null>(null);
  const [featuredStrategy, setFeaturedStrategy] = useState<AggregatedStrategy | null>(null);
  const [alternativeStrategies, setAlternativeStrategies] = useState<AggregatedStrategy[]>([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    const loadStrategies = async () => {
      try {
        setLoading(true);
        const response = await fetchAggregatorStrategies(
          API_BASE_URL,
          {
            chain: selectedChain || null,
            protocol: selectedProtocol || null,
            min_tvl: parseFloat(minTvl) || null,
            min_apy: parseFloat(minApy) || null,
            sort: sortBy,
            limit: 200,
            offset: 0,
          }
        );
        
        // Добавляем моки для volume_24h и fees_24h если их нет
        const strategiesWithMetrics = (response.items || []).map((strategy) => ({
          ...strategy,
          volume_24h: strategy.volume_24h ?? (strategy.tvl_usd * (0.1 + Math.random() * 0.3)), // 10-40% от TVL
          fees_24h: strategy.fees_24h ?? (strategy.tvl_usd * (0.001 + Math.random() * 0.002)), // 0.1-0.3% от TVL
        }));
        
        setStrategies(strategiesWithMetrics);
        
        // Устанавливаем featured strategy (первая в списке)
        if (strategiesWithMetrics.length > 0) {
          setFeaturedStrategy(strategiesWithMetrics[0]);
          setAlternativeStrategies(strategiesWithMetrics.slice(1, 4)); // Следующие 3 стратегии
        } else {
          setFeaturedStrategy(null);
          setAlternativeStrategies([]);
        }
      } catch (error) {
        console.error("Failed to load strategies:", error);
        setStrategies([]);
        setFeaturedStrategy(null);
        setAlternativeStrategies([]);
      } finally {
        setLoading(false);
      }
    };

    loadStrategies();
  }, [sortBy, minTvl, minApy, selectedChain, selectedProtocol]);

  const displayedStrategies = showAll ? strategies : strategies.slice(0, 4);
  const remainingCount = Math.max(0, strategies.length - 4);

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-4">
            Top DeFi Strategies
          </h1>
          <p className="font-inter text-white/80 text-lg">
            Advanced strategy filtering with AI-powered insights
          </p>
        </div>

        {/* Sorting Options */}
        <div className="card-genora mb-6">
          <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
            Sorting Options
          </h2>
          
          {/* Sort Tabs */}
          <div className="flex gap-2 mb-4">
            {([
              { value: "ai_score_desc", label: "AI Score" },
              { value: "apy_desc", label: "APY" },
              { value: "tvl_desc", label: "TVL" },
              { value: "tvl_growth_desc", label: "Рост TVL" },
            ] as { value: SortBy; label: string }[]).map((sort) => (
              <button
                key={sort.value}
                onClick={() => setSortBy(sort.value)}
                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                  sortBy === sort.value
                    ? "bg-[var(--neonAqua)] text-black"
                    : "bg-white/10 text-white/70 hover:text-white"
                }`}
              >
                {sort.label}
              </button>
            ))}
          </div>

          {/* Filters */}
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm text-white/70 mb-2">Мин. TVL ($)</label>
              <input
                type="number"
                value={minTvl}
                onChange={(e) => setMinTvl(e.target.value)}
                placeholder="0"
                className="w-full h-10 rounded-md border border-white/20 bg-black/50 px-3 text-sm text-white placeholder:text-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Мин. APY (%)</label>
              <input
                type="number"
                value={minApy}
                onChange={(e) => setMinApy(e.target.value)}
                placeholder="0"
                className="w-full h-10 rounded-md border border-white/20 bg-black/50 px-3 text-sm text-white placeholder:text-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-white/70">Loading strategies...</div>
        ) : strategies.length === 0 ? (
          <div className="text-center py-12 text-white/70">No strategies found</div>
        ) : (
          <>
            <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
              {/* Featured Strategy */}
              {featuredStrategy && (
                <div className="card-genora border-2 border-[var(--neonAqua)]/50">
                  <div className="mb-4">
                    <span className="text-xs text-[var(--neonAqua)] uppercase">Featured Strategy</span>
                  </div>
                  <div className="mb-4">
                    <h2 className="text-2xl font-bold text-white mb-2">
                      {featuredStrategy.token_pair || featuredStrategy.name}
                    </h2>
                    <p className="text-white/70 text-sm">
                      {featuredStrategy.protocol} • {featuredStrategy.chain}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-xs text-white/70 mb-1">APY</div>
                      <div className="text-2xl font-bold text-green-400">
                        {featuredStrategy.apy?.toFixed(2) || "0.00"}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/70 mb-1">TVL</div>
                      <div className="text-xl font-semibold text-white">
                        {featuredStrategy.tvl_usd?.toLocaleString(undefined, { maximumFractionDigits: 2 }) || "0"} $
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/70 mb-1">Volume (24h)</div>
                      <div className="text-lg font-medium text-white">
                        ${(featuredStrategy.volume_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/70 mb-1">Fees (24h)</div>
                      <div className="text-lg font-medium text-white">
                        ${(featuredStrategy.fees_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/70 mb-1">Risk</div>
                      <div className="text-lg font-medium text-white">
                        {featuredStrategy.risk_index?.toFixed(2) || "N/A"}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/70 mb-1">AI Score</div>
                      <div className="text-lg font-medium text-[var(--neonAqua)]">
                        {featuredStrategy.ai_score?.toFixed(2) || "0.00"}
                      </div>
                    </div>
                  </div>
                  <Link
                    href={`/strategies/${featuredStrategy.id}`}
                    className="inline-block px-6 py-3 bg-gradient-to-r from-[var(--neonAqua)] to-purple-500 text-black font-semibold rounded-lg hover:opacity-90 transition-opacity"
                  >
                    View Details →
                  </Link>
                </div>
              )}

              {/* Alternative Strategies */}
              <div className="card-genora">
                <h3 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                  Alternative Strategies
                </h3>
                <div className="space-y-4">
                  {alternativeStrategies.map((strategy) => (
                    <Link
                      key={strategy.id}
                      href={`/strategies/${strategy.id}`}
                      className="block border border-white/10 rounded-lg p-4 hover:border-[var(--neonAqua)]/50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-semibold text-white">
                            {strategy.token_pair || strategy.name}
                          </h4>
                          <p className="text-xs text-white/70">
                            {strategy.protocol} • {strategy.chain}
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-white/70">APY: </span>
                          <span className="text-green-400 font-semibold">
                            {strategy.apy?.toFixed(2) || "0.00"}%
                          </span>
                        </div>
                        <div>
                          <span className="text-white/70">TVL: </span>
                          <span className="text-white font-medium">
                            {strategy.tvl_usd?.toLocaleString(undefined, { maximumFractionDigits: 0 }) || "0"} $
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            {/* Show All Button */}
            {!showAll && strategies.length > 4 && (
              <div className="text-center mt-6">
                <button
                  onClick={() => setShowAll(true)}
                  className="px-8 py-3 bg-gradient-to-r from-[var(--neonAqua)] to-purple-500 text-black font-semibold rounded-lg hover:opacity-90 transition-opacity"
                >
                  Show All Strategies ({remainingCount} more)
                </button>
              </div>
            )}

            {/* All Strategies Table (when showAll is true) */}
            {showAll && strategies.length > 0 && (
              <div className="card-genora mt-6">
                <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
                  All Strategies ({strategies.length})
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="text-xs uppercase text-white/60 border-b border-white/10">
                      <tr>
                        <th className="py-3 text-left font-medium">Strategy</th>
                        <th className="py-3 text-left font-medium">Protocol</th>
                        <th className="py-3 text-left font-medium">Chain</th>
                        <th className="py-3 text-right font-medium">APY</th>
                        <th className="py-3 text-right font-medium">TVL</th>
                        <th className="py-3 text-right font-medium">Volume (24h)</th>
                        <th className="py-3 text-right font-medium">Fees (24h)</th>
                        <th className="py-3 text-right font-medium">Risk</th>
                        <th className="py-3 text-right font-medium">AI Score</th>
                        <th className="py-3 text-center font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {strategies.map((strategy) => (
                        <tr
                          key={strategy.id}
                          className="border-b border-white/10 hover:bg-white/5 transition-colors"
                        >
                          <td className="py-3 text-white font-medium">
                            {strategy.token_pair || strategy.name}
                          </td>
                          <td className="py-3 text-white/90">{strategy.protocol}</td>
                          <td className="py-3 text-white/90">{strategy.chain}</td>
                          <td className="py-3 text-right text-green-400 font-medium">
                            {strategy.apy?.toFixed(2) || "0.00"}%
                          </td>
                          <td className="py-3 text-right text-white/90">
                            ${strategy.tvl_usd?.toLocaleString(undefined, { maximumFractionDigits: 0 }) || "0"}
                          </td>
                          <td className="py-3 text-right text-white/90">
                            ${(strategy.volume_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                          </td>
                          <td className="py-3 text-right text-white/90">
                            ${(strategy.fees_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                          </td>
                          <td className="py-3 text-right text-white/90">
                            {strategy.risk_index?.toFixed(2) || "N/A"}
                          </td>
                          <td className="py-3 text-right text-[var(--neonAqua)] font-medium">
                            {strategy.ai_score?.toFixed(2) || "0.00"}
                          </td>
                          <td className="py-3 text-center">
                            <Link
                              href={`/strategies/${strategy.id}`}
                              className="text-[var(--neonAqua)] hover:underline text-xs"
                            >
                              View →
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
