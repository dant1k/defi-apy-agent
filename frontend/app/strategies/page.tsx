import { Metadata } from 'next';
import { Suspense } from "react";
import NextDynamic from "next/dynamic";
import { HomeSkeleton } from "../../components/home/home-skeleton";

export const dynamic = "force-static";
export const revalidate = 300;
const HomeClient = NextDynamic(
  () => import("../../components/home/home-client").then((mod) => mod.HomeClient),
  {
    ssr: false,
    loading: () => <HomeSkeleton />,
  },
);

export const metadata: Metadata = {
  title: "DeFi Strategies | DeFi APY Agent",
  description: "Подбор DeFi-стратегий и аналитика APY с минимальной задержкой",
};

export default function StrategiesPage(): JSX.Element {
  return (
    <Suspense fallback={<HomeSkeleton />}>
      <HomeClient />
    </Suspense>
  );
}
