"use client";

import { useEffect, useState } from "react";
import { Timeframe, getAptosDexes, type AptosDexSummary } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Props = {
  metric: "tvl" | "volume" | "fees";
  timeframe: Timeframe;
  selectedDex: string | null;
};

export function AptosOverview({ metric, timeframe, selectedDex }: Props) {
  const [data, setData] = useState<AptosDexSummary[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getAptosDexes({ sortBy: metric, timeframe })
      .then(setData)
      .catch((err) => {
        console.error("Failed to fetch Aptos DEX data:", err);
        setData([]);
      })
      .finally(() => setLoading(false));
  }, [metric, timeframe]);

  const chartData = data.map((dex) => ({
    name: dex.name,
    value:
      metric === "tvl"
        ? dex.tvl_usd
        : metric === "volume"
        ? dex.volume[timeframe]
        : dex.fees[timeframe],
  }));

  const totalTvl = data.reduce((sum, d) => sum + d.tvl_usd, 0);

  return (
    <div className="grid gap-4 md:grid-cols-[2fr,1fr]">
      <div className="card-genora h-72">
        <div className="h-full pt-4 px-4">
          {loading ? (
            <div className="flex h-full items-center justify-center text-sm text-white/70">
              Loading Aptos data...
            </div>
          ) : chartData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-white/70">
              No data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis 
                  dataKey="name" 
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  tick={{ fill: "#9ca3af", fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1f2937",
                    border: "1px solid #374151",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="var(--neonAqua)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card-genora h-72">
        <div className="flex h-full flex-col justify-between pt-4 px-4">
          <div>
            <p className="text-xs uppercase text-white/60 mb-2">
              Total Aptos TVL
            </p>
            <p className="text-2xl font-semibold text-[var(--neonAqua)]">
              ${totalTvl.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </p>
          </div>
          
          {selectedDex && (
            <div>
              <p className="text-xs uppercase text-white/60 mb-2">
                Selected DEX
              </p>
              <p className="text-sm text-white">{selectedDex}</p>
            </div>
          )}

          <div className="mt-auto pt-4">
            <p className="text-xs text-white/50">
              {data.length} DEX{data.length !== 1 ? "es" : ""} tracked
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
