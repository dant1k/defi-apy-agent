"use client";

import { useEffect, useState } from "react";
import {
  AptosDexSummary,
  Timeframe,
  getAptosDexes,
} from "@/lib/api";

type Props = {
  metric: "tvl" | "volume" | "fees";
  timeframe: Timeframe;
  onSelectDex: (slug: string | null) => void;
};

export function AptosDexTable({ metric, timeframe, onSelectDex }: Props) {
  const [data, setData] = useState<AptosDexSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

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

  const handleRowClick = (slug: string) => {
    const value = slug === selected ? null : slug;
    setSelected(value);
    onSelectDex(value);
  };

  return (
    <div className="card-genora">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-orbitron text-xl font-bold text-[var(--neonAqua)]">
          Aptos DEX
        </h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-xs uppercase text-white/60 border-b border-white/10">
            <tr>
              <th className="py-3 text-left font-medium">DEX</th>
              <th className="py-3 text-right font-medium">TVL</th>
              <th className="py-3 text-right font-medium">Volume 24h</th>
              <th className="py-3 text-right font-medium">Fees 24h</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-sm text-white/70">
                  Loading...
                </td>
              </tr>
            )}
            {!loading && data.length === 0 && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-sm text-white/70">
                  No data available
                </td>
              </tr>
            )}
            {!loading &&
              data.map((dex) => (
                <tr
                  key={dex.slug}
                  onClick={() => handleRowClick(dex.slug)}
                  className={`cursor-pointer border-b border-white/10 transition-colors ${
                    selected === dex.slug
                      ? "bg-[var(--neonAqua)]/20 hover:bg-[var(--neonAqua)]/30"
                      : "hover:bg-white/5"
                  }`}
                >
                  <td className="py-3 text-white font-medium">{dex.name}</td>
                  <td className="py-3 text-right text-white/90">
                    ${dex.tvl_usd.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 text-right text-white/90">
                    ${dex.volume["24h"].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 text-right text-white/90">
                    ${dex.fees["24h"].toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
