'use client';

import { Suspense, useEffect, useState } from "react";
import { StrategiesSkeleton } from "../home/home-skeleton";
import { fetchChains, fetchProtocols, fetchTopTokens } from "../../lib/api";
import type { TokenOption } from "../home/types";
import StrategiesPanel from "../home/strategies-panel";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export function StrategiesClient(): JSX.Element {
  const [chains, setChains] = useState<string[]>([]);
  const [protocols, setProtocols] = useState<string[]>([]);
  const [tokenOptions, setTokenOptions] = useState<TokenOption[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function preloadFilters() {
      try {
        const [chainItems, protocolItems, tokens] = await Promise.all([
          fetchChains(API_BASE_URL),
          fetchProtocols(API_BASE_URL),
          fetchTopTokens(API_BASE_URL, 100),
        ]);
        if (!cancelled) {
          setChains(chainItems);
          setProtocols(protocolItems);
          setTokenOptions((tokens || []).map((t) => ({ value: t.symbol, label: t.symbol, slug: t.slug })));
        }
      } catch (error) {
        if (process.env.NODE_ENV !== "production") {
          console.error("Failed to preload filters", error);
        }
        if (!cancelled) {
          setChains([]);
          setProtocols([]);
          setTokenOptions([]);
        }
      }
    }
    preloadFilters();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="min-h-screen bg-[var(--darkVoid)] pt-20">
      <div className="container mx-auto px-6 py-8">
        <div className="text-center mb-12">
          <h1 className="font-orbitron text-4xl font-bold text-[var(--neonAqua)] mb-4">
            DeFi Strategies
          </h1>
          <p className="font-inter text-white/80 text-lg">
            Advanced filtering and analysis for optimal yield strategies
          </p>
        </div>

        <div className="card-genora">
                 <Suspense fallback={<StrategiesSkeleton />}>
                   <StrategiesPanel
                     apiBaseUrl={API_BASE_URL}
                     chains={chains}
                     protocols={protocols}
                     tokens={tokenOptions.map(t => t.value)}
                   />
                 </Suspense>
        </div>
      </div>
    </div>
  );
}
