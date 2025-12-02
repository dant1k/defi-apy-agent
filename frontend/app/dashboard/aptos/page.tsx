"use client";

import { useState } from "react";
import { AptosDexTable } from "@/components/aptos/aptos-dex-table";
import { AptosPoolsTable } from "@/components/aptos/aptos-pools-table";
import { AptosOverview } from "@/components/aptos/aptos-overview";

type Metric = "tvl" | "volume" | "fees";
type Timeframe = "24h" | "7d" | "30d" | "all";

export default function AptosDashboardPage() {
  const [metric, setMetric] = useState<Metric>("tvl");
  const [timeframe, setTimeframe] = useState<Timeframe>("24h");
  const [selectedDex, setSelectedDex] = useState<string | null>(null);
  const [selectedPair, setSelectedPair] = useState<string | null>(null);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* header */}
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Aptos DEX Analytics</h1>
          <p className="text-sm text-white/70">
            TVL, volume and fees across Aptos DEX and pools
          </p>
        </div>
        
        {/* контролы метрика и таймфрейм */}
        <div className="flex gap-2">
          {/* metric toggle */}
          <div className="flex gap-1 bg-[var(--graphiteGray)] p-1 rounded">
            {(["tvl", "volume", "fees"] as Metric[]).map((m) => (
              <button
                key={m}
                onClick={() => setMetric(m)}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  metric === m
                    ? "bg-[var(--neonAqua)] text-black"
                    : "text-white/70 hover:text-white"
                }`}
              >
                {m.charAt(0).toUpperCase() + m.slice(1)}
              </button>
            ))}
          </div>
          
          {/* timeframe toggle */}
          <div className="flex gap-1 bg-[var(--graphiteGray)] p-1 rounded">
            {(["24h", "7d", "30d", "all"] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  timeframe === tf
                    ? "bg-[var(--neonAqua)] text-black"
                    : "text-white/70 hover:text-white"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* overview: график + карточки */}
      <AptosOverview
        metric={metric}
        timeframe={timeframe}
        selectedDex={selectedDex}
      />

      {/* таблица DEX */}
      <AptosDexTable
        metric={metric}
        timeframe={timeframe}
        onSelectDex={setSelectedDex}
      />

      {/* таблица пулов */}
      <AptosPoolsTable
        metric={metric}
        timeframe={timeframe}
        selectedDex={selectedDex}
        selectedPair={selectedPair}
        onSelectPair={setSelectedPair}
      />
    </div>
  );
}

