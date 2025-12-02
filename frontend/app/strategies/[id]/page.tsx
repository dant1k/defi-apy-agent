"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { fetchStrategyDetails } from "@/lib/api";
import type { StrategyDetail } from "@/components/home/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Metric = "tvl" | "volume" | "fees";

export default function StrategyDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const strategyId = params.id as string;

  const [strategyDetail, setStrategyDetail] = useState<StrategyDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [metric, setMetric] = useState<Metric>("tvl");
  const [timeframe, setTimeframe] = useState<"24h" | "7d" | "30d" | "all">("7d");

  useEffect(() => {
    if (!strategyId) return;

    setLoading(true);
    const apiBaseUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000";
    
    console.log("[StrategyDetails] Fetching strategy:", strategyId);
    console.log("[StrategyDetails] API Base URL:", apiBaseUrl);
    
    fetchStrategyDetails(apiBaseUrl, strategyId)
      .then((data) => {
        console.log("[StrategyDetails] Received data:", data);
        if (data && data.strategy) {
          setStrategyDetail(data);
        } else {
          console.warn("[StrategyDetails] Invalid data format:", data);
          setStrategyDetail(null);
        }
      })
      .catch((err) => {
        console.error("[StrategyDetails] Failed to fetch strategy:", err);
        console.error("[StrategyDetails] Error details:", err.message);
        setStrategyDetail(null);
      })
      .finally(() => setLoading(false));
  }, [strategyId]);

  // Генерируем исторические данные для графика
  const generateHistoricalData = () => {
    if (!strategyDetail?.strategy) return [];
    const days = timeframe === "24h" ? 24 : timeframe === "7d" ? 7 : timeframe === "30d" ? 30 : 90;
    const data = [];
    const baseValue =
      metric === "tvl"
        ? strategyDetail.strategy.tvl_usd
        : metric === "volume"
        ? (strategyDetail.strategy.volume_24h || 0) * (timeframe === "24h" ? 1 : timeframe === "7d" ? 7 : 30)
        : (strategyDetail.strategy.fees_24h || 0) * (timeframe === "24h" ? 1 : timeframe === "7d" ? 7 : 30);

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
        <div className="text-white/70">Loading strategy details...</div>
      </div>
    );
  }

  if (!strategyDetail?.strategy) {
    return (
      <div className="min-h-screen bg-[var(--darkVoid)] flex items-center justify-center">
        <div className="text-center">
          <div className="text-white/70 mb-4">Strategy not found</div>
          <button
            onClick={() => router.push("/strategies")}
            className="text-[var(--neonAqua)] hover:underline"
          >
            ← Back to Strategies
          </button>
        </div>
      </div>
    );
  }

  const strategy = strategyDetail.strategy;
  const currentValue =
    metric === "tvl"
      ? strategy.tvl_usd
      : metric === "volume"
      ? (strategy.volume_24h || 0) * (timeframe === "24h" ? 1 : timeframe === "7d" ? 7 : 30)
      : (strategy.fees_24h || 0) * (timeframe === "24h" ? 1 : timeframe === "7d" ? 7 : 30);

  // Расчет баланса (упрощенный, на основе TVL)
  const token0Balance = strategy.tvl_usd * 0.6; // Примерное распределение
  const token1Balance = strategy.tvl_usd * 0.4;
  const tokenPair = strategy.token_pair || strategy.name;
  const tokens = tokenPair.split("-");

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push("/strategies")}
            className="text-[var(--neonAqua)] hover:underline mb-4 inline-block"
          >
            ← Back to Strategies
          </button>
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-2">
            {tokenPair} Strategy
          </h1>
          <p className="text-white/70">{strategy.protocol} • {strategy.chain}</p>
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
              {(["24h", "7d", "30d", "all"] as const).map((tf) => (
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
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%" minHeight={256}>
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

          {/* Right: Strategy Info and Balance */}
          <div className="space-y-6">
            {/* Strategy Info */}
            <div className="card-genora">
              <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                Strategy Info
              </h2>
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-white/70 mb-1">Strategy Address</div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-white font-mono">
                      {strategy.id.slice(0, 6)}...{strategy.id.slice(-4)}
                    </span>
                    <button
                      onClick={() => navigator.clipboard.writeText(strategy.id)}
                      className="text-white/70 hover:text-white"
                      title="Copy address"
                    >
                      📋
                    </button>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-white/70 mb-1">Protocol</div>
                  <div className="text-sm text-white">{strategy.protocol}</div>
                </div>
                <div>
                  <div className="text-xs text-white/70 mb-1">Chain</div>
                  <div className="text-sm text-white">{strategy.chain}</div>
                </div>
              </div>
            </div>

            {/* Current Balance */}
            {strategy.token_pair && tokens.length >= 2 && (
              <div className="card-genora">
                <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                  Current Balance
                </h2>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-xs text-white">
                          {tokens[0]?.[0] || "T"}
                        </div>
                        <span className="text-sm text-white">{tokens[0] || "Token0"}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-white font-medium">
                          ${(token0Balance / 1e6).toFixed(2)}M
                        </div>
                        <div className="text-xs text-white/70">
                          {((token0Balance / strategy.tvl_usd) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-xs text-white">
                          {tokens[1]?.[0] || "T"}
                        </div>
                        <span className="text-sm text-white">{tokens[1] || "Token1"}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-white font-medium">
                          ${(token1Balance / 1e3).toFixed(2)}K
                        </div>
                        <div className="text-xs text-white/70">
                          {((token1Balance / strategy.tvl_usd) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Balance Visualization */}
                  <div className="mt-4">
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden flex">
                      <div
                        className="bg-blue-500"
                        style={{ width: `${(token0Balance / strategy.tvl_usd) * 100}%` }}
                      />
                      <div
                        className="bg-green-500"
                        style={{ width: `${(token1Balance / strategy.tvl_usd) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Strategy Statistics */}
            <div className="card-genora">
              <h2 className="font-orbitron text-lg font-bold text-[var(--neonAqua)] mb-4">
                Strategy Statistics
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">APY</span>
                  <span className="text-sm text-white">{strategy.apy?.toFixed(2) || "0.00"}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Total Volume (All)</span>
                  <span className="text-sm text-white">
                    ${((strategy.volume_24h || 0) * 30).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Total Fees (All)</span>
                  <span className="text-sm text-white">
                    ${((strategy.fees_24h || 0) * 30).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Volume (24h)</span>
                  <span className="text-sm text-white">
                    ${(strategy.volume_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Fees (24h)</span>
                  <span className="text-sm text-white">
                    ${(strategy.fees_24h || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">Risk Index</span>
                  <span className="text-sm text-white">{strategy.risk_index?.toFixed(2) || "N/A"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-white/70">AI Score</span>
                  <span className="text-sm text-[var(--neonAqua)]">{strategy.ai_score?.toFixed(2) || "0.00"}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
