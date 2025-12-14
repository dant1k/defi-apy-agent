"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import TerminalLayout from "@/components/TerminalLayout";
import KPIHeader from "@/components/KPIHeader";
import ChartCard from "@/components/ChartCard";
import Tabs from "@/components/Tabs";
import LoadingState from "@/components/LoadingState";
import EmptyState from "@/components/EmptyState";
import DataTable from "@/components/DataTable";
import { fetchDexDetail, fetchDexPools } from "@/lib/api";

export default function DexDetailPage({ params }: { params: { dex_slug: string } }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [search, setSearch] = useState("");
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["dex", params.dex_slug],
    queryFn: () => fetchDexDetail(params.dex_slug),
  });

  const { data: poolsData, isLoading: poolsLoading } = useQuery({
    queryKey: ["dex-pools", params.dex_slug, search],
    queryFn: () => fetchDexPools(params.dex_slug, { search, sort: "tvl_desc" }),
    enabled: activeTab === "pools",
  });

  return (
    <TerminalLayout>
      <div className="container mx-auto px-4 py-6">
        <KPIHeader
          title={data?.name || params.dex_slug}
          updatedAt={data?.updated_at}
          warning={data?.warning}
        />

        {isLoading ? (
          <LoadingState />
        ) : error ? (
          <EmptyState message="Error loading DEX" />
        ) : !data ? (
          <EmptyState message="DEX not found" />
        ) : (
          <>
            <Tabs
              tabs={[
                { id: "overview", label: "Overview" },
                { id: "pools", label: "Pools" },
              ]}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />

            {activeTab === "overview" && (
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
              </div>
            )}

            {activeTab === "pools" && (
              <div className="mt-6">
                {poolsLoading ? (
                  <LoadingState />
                ) : (
                  <>
                    <input
                      type="text"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Search pools..."
                      className="border rounded px-3 py-2 mb-4 w-full"
                    />
                    <DataTable
                      data={poolsData?.items || []}
                      columns={[
                        { key: "pool", label: "Pool" },
                        { key: "tvl_usd", label: "TVL" },
                        { key: "volume_24h_usd", label: "Volume (24H)" },
                        { key: "fees_24h_usd", label: "Fees (24H)" },
                      ]}
                      onRowClick={(row) => {
                        window.location.href = `/terminal/aptos/dex/${params.dex_slug}/pool/${row.id}`;
                      }}
                    />
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </TerminalLayout>
  );
}

