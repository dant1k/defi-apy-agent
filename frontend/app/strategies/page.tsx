import { Metadata } from 'next';
import { Suspense } from "react";
import { StrategiesSkeleton } from "../../components/home/home-skeleton";
import StrategiesPanel from "../../components/home/strategies-panel";
import { fetchChains, fetchProtocols, fetchTopTokens } from "../../lib/api";

export const metadata: Metadata = {
  title: "DeFi Strategies | Genora",
  description: "Advanced DeFi strategy filtering and analysis with AI-powered insights",
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

async function getFilterData() {
  try {
    const [chains, protocols, tokens] = await Promise.all([
      fetchChains(API_BASE_URL),
      fetchProtocols(API_BASE_URL),
      fetchTopTokens(API_BASE_URL, 100),
    ]);
    return {
      chains,
      protocols,
      tokens: (tokens || []).map((t) => t.symbol),
    };
  } catch (error) {
    console.error("Failed to load filter data:", error);
    return {
      chains: [],
      protocols: [],
      tokens: [],
    };
  }
}

export default async function StrategiesPage(): Promise<JSX.Element> {
  const { chains, protocols, tokens } = await getFilterData();

  return (
    <div className="min-h-screen bg-[var(--darkVoid)]">
      <div className="container mx-auto px-6 py-8">
        <Suspense fallback={<StrategiesSkeleton />}>
          <StrategiesPanel
            apiBaseUrl={API_BASE_URL}
            chains={chains}
            protocols={protocols}
            tokens={tokens}
          />
        </Suspense>
      </div>
    </div>
  );
}
