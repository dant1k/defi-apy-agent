"use client";

import { useQuery } from "@tanstack/react-query";
import TerminalLayout from "@/components/TerminalLayout";
import KPIHeader from "@/components/KPIHeader";
import ChartCard from "@/components/ChartCard";
import LoadingState from "@/components/LoadingState";
import EmptyState from "@/components/EmptyState";
import { fetchPoolDetail } from "@/lib/api";

export default function PoolDetailPage({
  params,
}: {
  params: { dex_slug: string; pool_id: string };
}) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["pool", params.dex_slug, params.pool_id],
    queryFn: () => fetchPoolDetail(params.dex_slug, params.pool_id),
  });

  return (
    <TerminalLayout>
      <div className="container mx-auto px-4 py-6">
        <KPIHeader
          title={`${data?.token0_symbol || ""} / ${data?.token1_symbol || ""}`}
          updatedAt={data?.updated_at}
          warning={data?.warning}
        />

        {isLoading ? (
          <LoadingState />
        ) : error ? (
          <EmptyState message="Error loading pool" />
        ) : !data ? (
          <EmptyState message="Pool not found" />
        ) : (
          <div className="mt-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">TVL</div>
                <div className="text-2xl font-bold">
                  ${data.tvl_usd?.toLocaleString() || "—"}
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">Volume 24h</div>
                <div className="text-2xl font-bold">
                  ${data.volume_24h_usd?.toLocaleString() || "—"}
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <div className="text-sm text-gray-500">Fees 24h</div>
                <div className="text-2xl font-bold">
                  ${data.fees_24h_usd?.toLocaleString() || "—"}
                </div>
              </div>
            </div>

            <ChartCard
              title="TVL 30 Days"
              data={data.charts_30d || []}
              dataKey="tvl_usd"
            />

            <ChartCard
              title="Volume 30 Days"
              data={data.charts_30d || []}
              dataKey="volume_24h_usd"
            />
          </div>
        )}
      </div>
    </TerminalLayout>
  );
}

