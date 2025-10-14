'use client';

import { Suspense, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { StrategyCacheEntry, TokenOption } from "./types";
import { AnalyticsSkeleton, StrategiesSkeleton } from "./home-skeleton";

const StrategiesPanel = dynamic(() => import("./strategies-panel"), {
  ssr: false,
  suspense: true,
});

const AnalyticsPanel = dynamic(() => import("./analytics-panel"), {
  ssr: false,
  suspense: true,
});

const FALLBACK_TOKENS: TokenOption[] = [
  { value: "USDT", label: "USDT" },
  { value: "USDC", label: "USDC" },
  { value: "ETH", label: "ETH" },
  { value: "APT", label: "APT" },
  { value: "SUI", label: "SUI" },
];

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export function HomeClient(): JSX.Element {
  const [activeView, setActiveView] = useState<"strategies" | "analytics">("strategies");
  const [tokenOptions, setTokenOptions] = useState<TokenOption[]>(FALLBACK_TOKENS);
  const [strategyCache, setStrategyCache] = useState<Record<string, StrategyCacheEntry>>({});

  useEffect(() => {
    let cancelled = false;
    async function fetchTokens() {
      try {
        const res = await fetch(`${API_BASE_URL}/tokens`, {
          cache: "force-cache",
        });
        if (!res.ok) {
          throw new Error("failed to fetch");
        }
        const data = (await res.json()) as {
          tokens: { symbol: string; name: string; slug?: string }[];
        };
        if (cancelled) return;
        if (Array.isArray(data.tokens) && data.tokens.length > 0) {
          const next = data.tokens
            .map((item) => ({
              value: item.symbol.toUpperCase(),
              label: `${item.symbol.toUpperCase()} · ${item.name}`,
              slug: item.slug,
            }))
            .slice(0, 100);
          setTokenOptions(next);
        }
      } catch (fetchError) {
        if (process.env.NODE_ENV !== "production") {
          console.error("Failed to fetch token list, using fallback", fetchError);
        }
        if (!cancelled) {
          setTokenOptions(FALLBACK_TOKENS);
        }
      }
    }
    fetchTokens();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    void import("./strategies-panel");
  }, []);

  useEffect(() => {
    if (activeView === "analytics") {
      void import("./analytics-panel");
    }
  }, [activeView]);

  return (
    <section className="page">
      <div className="view-switcher">
        <button
          type="button"
          className={activeView === "strategies" ? "active" : ""}
          onClick={() => setActiveView("strategies")}
        >
          Поиск стратегий
        </button>
        <button
          type="button"
          className={activeView === "analytics" ? "active" : ""}
          onClick={() => setActiveView("analytics")}
        >
          Новые пулы
        </button>
      </div>

      {activeView === "strategies" && (
        <Suspense fallback={<StrategiesSkeleton />}>
          <StrategiesPanel
            tokenOptions={tokenOptions}
            apiBaseUrl={API_BASE_URL}
            cache={strategyCache}
            onCacheUpdate={(key, entry) =>
              setStrategyCache((prev) => ({
                ...prev,
                [key]: entry,
              }))
            }
          />
        </Suspense>
      )}

      {activeView === "analytics" && (
        <Suspense fallback={<AnalyticsSkeleton />}>
          <AnalyticsPanel tokenOptions={tokenOptions} apiBaseUrl={API_BASE_URL} />
        </Suspense>
      )}
    </section>
  );
}
