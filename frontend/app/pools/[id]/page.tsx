"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { getAptosPoolById, type AptosPoolSummary, Timeframe } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

type Metric = "tvl" | "volume" | "fees";

export default function PoolDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const poolId = params.id as string;

  const [pool, setPool] = useState<AptosPoolSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [metric, setMetric] = useState<Metric>("tvl");
  const [timeframe, setTimeframe] = useState<Timeframe>("7d");

  useEffect(() => {
    if (!poolId) return;

    setLoading(true);
    getAptosPoolById(poolId)
      .then((data) => {
        if (data) {
          setPool(data);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch pool:", err);
      })
      .finally(() => setLoading(false));
  }, [poolId]);

  // Генерируем исторические данные для графика (мок)
  const generateHistoricalData = () => {
    if (!pool) return [];
    const days = timeframe === "24h" ? 24 : timeframe === "7d" ? 7 : timeframe === "30d" ? 30 : 90;
    const data = [];
    const baseValue =
      metric === "tvl"
        ? pool.tvl_usd
        : metric === "volume"
        ? pool.volume[timeframe]
        : pool.fees[timeframe];

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const variation = 0.8 + Math.random() * 0.4; // 80-120% variation
      data.push({
        date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        value: baseValue * variation,
      });
    }
    return data;
  };

  const chartData = generateHistoricalData();

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--darkVoid)] flex items-center justify-center">
        <div className="text-white/70">Loading pool details...</div>
      </div>
    );
  }

  if (!pool) {
    return (
      <div className="min-h-screen bg-[var(--darkVoid)] flex items-center justify-center">
        <div className="text-center">
          <div className="text-white/70 mb-4">Pool not found</div>
          <button
            onClick={() => router.push("/pools")}
            className="text-[var(--neonAqua)] hover:underline"
          >
            ← Back to Pools
          </button>
        </div>
      </div>
    );
  }

  const currentValue =
    metric === "tvl"
      ? pool.tvl_usd
      : metric === "volume"
      ? pool.volume[timeframe]
      : pool.fees[timeframe];

  // Расчет баланса (упрощенный, на основе TVL)
  const token0Balance = pool.tvl_usd * 0.6; // Примерное распределение
  const token1Balance = pool.tvl_usd * 0.4;

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push("/pools")}
            className="text-[var(--neonAqua)] hover:underline mb-4 inline-block"
          >
            ← Back to Pools
          </button>
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-2">
            {pool.token0}/{pool.token1} Pool
          </h1>
          <p className="text-white/70">{pool.dex_slug} • Fee Tier: {(pool.fee_tier * 100).toFixed(2)}%</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-4 mb-6 border-b border-white/10">
          <button className="px-4 py-2 text-sm font-medium text-white border-b-2 border-[var(--neonAqua)]">
            Analytics
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
          {/* Left: Chart Section */}
          <div className="card-genora">
            {/* Metric Toggle */}
            <div className="flex gap-2 mb-4">
              {(["tvl", "volume", "fees"] as Metric[]).map((m) => (
                <button
                  key={m}
                  onClick={() => setMetric(m)}
                  className={`px-4 py-2 text-sm font-medium rounded transition-colors ${
                    metric === m
                      ? "bg-[var(--neonAqua)] text-black"
                      : "bg-white/10 text-white/70 hover:text-white"
                  }`}
                >
                  {m === "tvl" ? "TVL" : m.charAt(0).toUpperCase() + m.slice(1)}
                </button>
              ))}
            </div>

            {/* Value Display */}
            <div className="mb-4">
              <div className="text-sm text-white/70 mb-1">
                {metric === "tvl" ? "Total Value Locked" : metric === "volume" ? "Volume" : "Fees"}
              </div>
              <div className="text-3xl font-bold text-white">
                ${currentValue.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-white/50 mt-1">
                {timeframe === "24h"
                  ? "Last 24 hours"
                  : timeframe === "7d"
                  ? "Last 7 days"
                  : timeframe === "30d"
                  ? "Last 30 days"
                  : "All time"}
              </div>
            </div>

            {/* Timeframe Toggle */}
            <div className="flex gap-2 mb-4">
              {(["24h", "7d", "30d", "all"] as Timeframe[]).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                    timeframe === tf
                      ? "bg-[var(--neonAqua)] text-black"
                      : "bg-white/10 text-white/70 hover:text-white"
                  }`}
                >
                  {tf === "all" ? "All" : tf}
                </button>
              ))}
            </div>

            {/* Chart */}
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#9ca3af", fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1f2937",
                      border: "1px solid #374151",
                      borderRadius: "8px",
                      color: "#fff",
                    }}
                  />
                  <Bar dataKey="value" fill="var(--neonAqua)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right: Pool Info and Balance */}
          <div className="space-y-6">
            {/* Pool Info */}
            <div className="card-genora">
              <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                Pool Info
              </h2>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-white/70 mb-1">Pool Address</div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-white font-mono">
                      {pool.address.slice(0, 6)}...{pool.address.slice(-4)}
                    </span>
                    <button
                      onClick={() => navigator.clipboard.writeText(pool.address)}
                      className="text-white/70 hover:text-white"
                      title="Copy address"
                    >
                      📋
                    </button>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-white/70 mb-1">Fee Tier</div>
                  <div className="text-sm text-white">{(pool.fee_tier * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-xs text-white/70 mb-1">DEX</div>
                  <div className="text-sm text-white">{pool.dex_slug}</div>
                </div>
              </div>
            </div>

            {/* Current Balance */}
            <div className="card-genora">
              <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                Current Balance
              </h2>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-xs text-white">
                        {pool.token0[0]}
                      </div>
                      <span className="text-sm text-white">{pool.token0}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-white font-medium">
                        ${(token0Balance / 1e6).toFixed(2)}M
                      </div>
                      <div className="text-xs text-white/70">
                        {((token0Balance / pool.tvl_usd) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-xs text-white">
                        {pool.token1[0]}
                      </div>
                      <span className="text-sm text-white">{pool.token1}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-white font-medium">
                        ${(token1Balance / 1e3).toFixed(2)}K
                      </div>
                      <div className="text-xs text-white/70">
                        {((token1Balance / pool.tvl_usd) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
                {/* Balance Visualization */}
                <div className="mt-4">
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden flex">
                    <div
                      className="bg-blue-500"
                      style={{ width: `${(token0Balance / pool.tvl_usd) * 100}%` }}
                    />
                    <div
                      className="bg-green-500"
                      style={{ width: `${(token1Balance / pool.tvl_usd) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Pool Stats */}
            <div className="card-genora">
              <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                Pool Statistics
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">APR (Fee)</span>
                  <span className="text-sm text-white">{(pool.apr_fee * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Total Volume (All)</span>
                  <span className="text-sm text-white">
                    ${pool.volume.all.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Total Fees (All)</span>
                  <span className="text-sm text-white">
                    ${pool.fees.all.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

