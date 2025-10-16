'use client';

import { Suspense, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { StrategiesSkeleton } from "./home-skeleton";
import { fetchChains, fetchProtocols, fetchTopTokens } from "../../lib/api";
import type { TokenOption } from "./types";

const StrategiesPanel = dynamic(() => import("./strategies-panel"), {
  ssr: false,
  suspense: true,
});

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export function HomeClient(): JSX.Element {
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
    <section className="page">
      <Suspense fallback={<StrategiesSkeleton />}>
        <StrategiesPanel
          apiBaseUrl={API_BASE_URL}
          chains={chains}
          protocols={protocols}
          tokens={tokenOptions.map((t) => t.value)}
        />
      </Suspense>
    </section>
  );
}
