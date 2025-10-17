import { Metadata } from 'next';
import { Suspense } from "react";
import NextDynamic from "next/dynamic";
import { HomeSkeleton } from "../../components/home/home-skeleton";

export const dynamic = "force-static";
export const revalidate = 300;
const StrategiesClient = NextDynamic(
  () => import("../../components/strategies/strategies-client").then((mod) => mod.StrategiesClient),
  {
    ssr: false,
    loading: () => <HomeSkeleton />,
  },
);

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
