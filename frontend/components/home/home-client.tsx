'use client';

import { Suspense, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { StrategiesSkeleton } from "./home-skeleton";
import { fetchChains, fetchProtocols } from "../../lib/api";

const StrategiesPanel = dynamic(() => import("./strategies-panel"), {
  ssr: false,
  suspense: true,
});

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export function HomeClient(): JSX.Element {
  const [chains, setChains] = useState<string[]>([]);
  const [protocols, setProtocols] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function preloadFilters() {
      try {
        const [chainItems, protocolItems] = await Promise.all([
          fetchChains(API_BASE_URL),
          fetchProtocols(API_BASE_URL),
        ]);
        if (!cancelled) {
          setChains(chainItems);
          setProtocols(protocolItems);
        }
      } catch (error) {
        if (process.env.NODE_ENV !== "production") {
          console.error("Failed to preload filters", error);
        }
        if (!cancelled) {
          setChains([]);
          setProtocols([]);
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
        <StrategiesPanel apiBaseUrl={API_BASE_URL} chains={chains} protocols={protocols} />
      </Suspense>
    </section>
  );
}
