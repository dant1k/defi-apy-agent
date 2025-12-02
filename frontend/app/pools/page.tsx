"use client";

import { useState, useEffect } from "react";
import { getAptosPools, getAptosDexes, type AptosPoolSummary, type AptosDexSummary, Timeframe } from "@/lib/api";
import Link from "next/link";

type SortBy = "tvl" | "volume" | "fees" | "apr";
type Metric = "tvl" | "volume" | "fees";

export default function PoolsPage() {
  const [pools, setPools] = useState<AptosPoolSummary[]>([]);
  const [dexes, setDexes] = useState<AptosDexSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortBy>("apr");
  const [timeframe, setTimeframe] = useState<Timeframe>("24h");
  const [selectedDex, setSelectedDex] = useState<string | null>(null);
  const [searchPair, setSearchPair] = useState("");
  const [minTvl, setMinTvl] = useState<string>("0");
  const [minApr, setMinApr] = useState<string>("0");
  const [featuredPool, setFeaturedPool] = useState<AptosPoolSummary | null>(null);
  const [alternativePools, setAlternativePools] = useState<AptosPoolSummary[]>([]);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getAptosDexes({ sortBy: "tvl", timeframe }),
      getAptosPools({
        dex: selectedDex || undefined,
        pair: searchPair || undefined,
        sortBy,
        timeframe,
        minTvl: parseFloat(minTvl) || 0,
        minApr: parseFloat(minApr) || 0,
      }),
    ])
      .then(([dexData, poolData]) => {
        setDexes(dexData);
        setPools(poolData);
        
        // Устанавливаем featured pool (первый в списке)
        if (poolData.length > 0) {
          setFeaturedPool(poolData[0]);
          setAlternativePools(poolData.slice(1, 4)); // Следующие 3 пула
        } else {
          setFeaturedPool(null);
          setAlternativePools([]);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch data:", err);
        setPools([]);
        setDexes([]);
        setFeaturedPool(null);
        setAlternativePools([]);
      })
      .finally(() => setLoading(false));
  }, [sortBy, timeframe, selectedDex, searchPair, minTvl, minApr]);

  const availableDexes = dexes.map((d) => d.slug);
  const displayedPools = showAll ? pools : pools.slice(0, 4);
  const remainingCount = pools.length - 4;

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-4">
            Aptos Liquidity Pools
          </h1>
          <p className="font-inter text-white/80 text-lg">
            Track DEX protocols and their liquidity pools on Aptos
          </p>
        </div>

        {/* Sorting Options */}
        <div className="card-genora mb-6">
          <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
            Sorting Options
          </h2>
          
          {/* Sort Tabs */}
          <div className="flex gap-2 mb-4">
            {(["apr", "tvl", "volume", "fees"] as SortBy[]).map((sort) => (
              <button
                key={sort}
                onClick={() => setSortBy(sort)}
                className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                  sortBy === sort
                    ? "bg-[var(--neonAqua)] text-black"
                    : "bg-white/10 text-white/70 hover:text-white"
                }`}
              >
                {sort === "apr" ? "APR" : sort === "tvl" ? "TVL" : sort.charAt(0).toUpperCase() + sort.slice(1)}
              </button>
            ))}
          </div>

          {/* Filters */}
          <div className="grid gap-4 md:grid-cols-4">
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
              <label className="block text-sm text-white/70 mb-2">Мин. APR (%)</label>
              <input
                type="number"
                value={minApr}
                onChange={(e) => setMinApr(e.target.value)}
                placeholder="0"
                className="w-full h-10 rounded-md border border-white/20 bg-black/50 px-3 text-sm text-white placeholder:text-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">Search Pair</label>
              <input
                type="text"
                value={searchPair}
                onChange={(e) => setSearchPair(e.target.value)}
                placeholder="e.g., APT USDC"
                className="w-full h-10 rounded-md border border-white/20 bg-black/50 px-3 text-sm text-white placeholder:text-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-2">DEX</label>
              <select
                value={selectedDex || ""}
                onChange={(e) => setSelectedDex(e.target.value || null)}
                className="w-full h-10 rounded-md border border-white/20 bg-black/50 px-3 text-sm text-white focus:border-[var(--neonAqua)] focus:outline-none"
              >
                <option value="">All DEXes</option>
                {availableDexes.map((dex) => (
                  <option key={dex} value={dex}>
                    {dex}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-white/70">Loading pools...</div>
        ) : pools.length === 0 ? (
          <div className="text-center py-12 text-white/70">No pools found</div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
            {/* Featured Strategy */}
            {featuredPool && (
              <div className="card-genora border-2 border-[var(--neonAqua)]/50">
                <div className="mb-4">
                  <span className="text-xs text-[var(--neonAqua)] uppercase">Featured Strategy</span>
                </div>
                <div className="mb-4">
                  <h2 className="text-2xl font-bold text-white mb-2">{featuredPool.pair}</h2>
                  <p className="text-white/70 text-sm">
                    {featuredPool.dex_slug.charAt(0).toUpperCase() + featuredPool.dex_slug.slice(1)} • Aptos
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-white/70 mb-1">APY</div>
                    <div className="text-2xl font-bold text-green-400">
                      {(featuredPool.apr_fee * 100).toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-white/70 mb-1">TVL</div>
                    <div className="text-xl font-semibold text-white">
                      {featuredPool.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 2 })} $
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-white/70 mb-1">Volume ({timeframe})</div>
                    <div className="text-lg font-medium text-white">
                      ${featuredPool.volume[timeframe].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-white/70 mb-1">Fees ({timeframe})</div>
                    <div className="text-lg font-medium text-white">
                      ${featuredPool.fees[timeframe].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  </div>
                </div>
                <Link
                  href={`/pools/${featuredPool.id}`}
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
                {alternativePools.map((pool) => (
                  <Link
                    key={pool.id}
                    href={`/pools/${pool.id}`}
                    className="block border border-white/10 rounded-lg p-4 hover:border-[var(--neonAqua)]/50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-white">{pool.pair}</h4>
                        <p className="text-xs text-white/70">
                          {pool.dex_slug.charAt(0).toUpperCase() + pool.dex_slug.slice(1)} • Aptos
                        </p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-white/70">APY: </span>
                        <span className="text-green-400 font-semibold">
                          {(pool.apr_fee * 100).toFixed(2)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-white/70">TVL: </span>
                        <span className="text-white font-medium">
                          {pool.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })} $
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Show All Button */}
        {!showAll && pools.length > 4 && (
          <div className="text-center mt-6">
            <button
              onClick={() => setShowAll(true)}
              className="px-8 py-3 bg-gradient-to-r from-[var(--neonAqua)] to-purple-500 text-black font-semibold rounded-lg hover:opacity-90 transition-opacity"
            >
              Show All Strategies ({remainingCount} more)
            </button>
          </div>
        )}

        {/* All Pools Table (when showAll is true) */}
        {showAll && pools.length > 0 && (
          <div className="card-genora mt-6">
            <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)] mb-4">
              All Pools ({pools.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs uppercase text-white/60 border-b border-white/10">
                  <tr>
                    <th className="py-3 text-left font-medium">Pool</th>
                    <th className="py-3 text-left font-medium">DEX</th>
                    <th className="py-3 text-right font-medium">TVL</th>
                    <th className="py-3 text-right font-medium">APR</th>
                    <th className="py-3 text-right font-medium">Volume {timeframe}</th>
                    <th className="py-3 text-right font-medium">Fees {timeframe}</th>
                    <th className="py-3 text-center font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pools.map((pool) => (
                    <tr
                      key={pool.id}
                      className="border-b border-white/10 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-3 text-white font-medium">{pool.pair}</td>
                      <td className="py-3 text-white/90">{pool.dex_slug}</td>
                      <td className="py-3 text-right text-white/90">
                        ${pool.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </td>
                      <td className="py-3 text-right text-green-400 font-medium">
                        {(pool.apr_fee * 100).toFixed(2)}%
                      </td>
                      <td className="py-3 text-right text-white/90">
                        ${pool.volume[timeframe].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </td>
                      <td className="py-3 text-right text-white/90">
                        ${pool.fees[timeframe].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </td>
                      <td className="py-3 text-center">
                        <Link
                          href={`/pools/${pool.id}`}
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
      </div>
    </div>
  );
}
