import { Metadata } from 'next';
import { Suspense } from "react";
import { HomeSkeleton } from "../../components/home/home-skeleton";
import { StrategiesClient } from "../../components/strategies/strategies-client";

export const metadata: Metadata = {
  title: "DeFi Strategies | Genora",
  description: "Advanced DeFi strategy filtering and analysis with AI-powered insights",
};

export default function StrategiesPage(): JSX.Element {
  return (
    <Suspense fallback={<HomeSkeleton />}>
      <StrategiesClient />
    </Suspense>
  );
}
