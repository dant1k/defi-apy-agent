"use client";

import { useEffect, useState } from "react";
import {
  AptosPoolSummary,
  Timeframe,
  getAptosPools,
} from "@/lib/api";

type Props = {
  metric: "tvl" | "volume" | "fees";
  timeframe: Timeframe;
  selectedDex: string | null;
  selectedPair: string | null;
  onSelectPair: (pair: string | null) => void;
};

export function AptosPoolsTable({
  metric,
  timeframe,
  selectedDex,
  selectedPair,
  onSelectPair,
}: Props) {
  const [data, setData] = useState<AptosPoolSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [pairFilter, setPairFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    getAptosPools({
      dex: selectedDex ?? undefined,
      pair: pairFilter || undefined,
      sortBy: metric === "tvl" ? "tvl" : metric === "volume" ? "volume" : "fees",
      timeframe,
    })
      .then(setData)
      .catch((err) => {
        console.error("Failed to fetch Aptos pools data:", err);
        setData([]);
      })
      .finally(() => setLoading(false));
  }, [metric, timeframe, selectedDex, pairFilter]);

  const handleRowClick = (pair: string) => {
    const value = pair === selectedPair ? null : pair;
    onSelectPair(value);
  };

  return (
    <div className="card-genora">
      <div className="mb-4 flex items-center justify-between gap-2">
        <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)]">
          Pools
        </h2>
        <input
          value={pairFilter}
          onChange={(e) => setPairFilter(e.target.value)}
          placeholder="Search pair (e.g., APT USDC)"
          className="h-8 w-48 rounded-md border border-white/20 bg-black/50 px-3 text-xs text-white placeholder:text-white/50 focus:border-[var(--neonAqua)] focus:outline-none"
        />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-xs uppercase text-white/60 border-b border-white/10">
            <tr>
              <th className="py-3 text-left font-medium">Pool</th>
              <th className="py-3 text-left font-medium">DEX</th>
              <th className="py-3 text-right font-medium">TVL</th>
              <th className="py-3 text-right font-medium">Volume 24h</th>
              <th className="py-3 text-right font-medium">Fees 24h</th>
              <th className="py-3 text-right font-medium">APR</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-sm text-white/70">
                  Loading...
                </td>
              </tr>
            )}
            {!loading && data.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-sm text-white/70">
                  No pools found
                </td>
              </tr>
            )}
            {!loading &&
              data.map((pool) => (
                <tr
                  key={pool.id}
                  onClick={() => handleRowClick(pool.pair)}
                  className={`cursor-pointer border-b border-white/10 transition-colors ${
                    selectedPair === pool.pair
                      ? "bg-[var(--neonAqua)]/20 hover:bg-[var(--neonAqua)]/30"
                      : "hover:bg-white/5"
                  }`}
                >
                  <td className="py-3 text-white font-medium">
                    {pool.token0}/{pool.token1} {(pool.fee_tier * 100).toFixed(2)}%
                  </td>
                  <td className="py-3 text-white/90">{pool.dex_slug}</td>
                  <td className="py-3 text-right text-white/90">
                    ${pool.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 text-right text-white/90">
                    ${pool.volume["24h"].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 text-right text-white/90">
                    ${pool.fees["24h"].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 text-right text-[var(--neonAqua)] font-medium">
                    {(pool.apr_fee * 100).toFixed(2)}%
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
