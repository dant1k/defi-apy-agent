"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import TerminalLayout from "@/components/TerminalLayout";
import FiltersBar from "@/components/FiltersBar";
import DataTable from "@/components/DataTable";
import KPIHeader from "@/components/KPIHeader";
import LoadingState from "@/components/LoadingState";
import EmptyState from "@/components/EmptyState";
import { fetchDexes } from "@/lib/api";
import { useDebounce } from "@/lib/hooks/useDebounce";

export default function DexListPage() {
  const [timeframe, setTimeframe] = useState("1d");
  const [sort, setSort] = useState("tvl_desc");
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading, error } = useQuery({
    queryKey: ["dexes", "aptos", sort, debouncedSearch],
    queryFn: () => fetchDexes({ chain: "aptos", sort }),
  });

  // Debug: log data when it changes
  if (data && process.env.NODE_ENV !== "production") {
    console.log("DEXes data:", data);
  }

  return (
    <TerminalLayout>
      <div className="container mx-auto px-4 py-6">
        <KPIHeader
          title="Aptos DEXes"
          updatedAt={data?.updated_at}
          warning={data?.warning}
        />
        
        <FiltersBar
          timeframe={timeframe}
          onTimeframeChange={setTimeframe}
          sort={sort}
          onSortChange={setSort}
          search={search}
          onSearchChange={setSearch}
        />

        {isLoading ? (
          <LoadingState />
        ) : error ? (
          <EmptyState message="Error loading DEXes" />
        ) : data?.items?.length === 0 ? (
          <EmptyState message="No DEXes found" />
        ) : (
          <div>
            <div className="mb-4 text-sm text-gray-600">
              Найдено DEXes: {data?.total || 0}
            </div>
            <DataTable
              data={data?.items || []}
              columns={[
                { key: "name", label: "DEX Name" },
                { key: "chain", label: "Chain" },
                { key: "tvl_usd", label: "TVL (USD)" },
                { key: "volume_24h_usd", label: "Volume 24h (USD)" },
                { key: "fees_24h_usd", label: "Fees 24h (USD)" },
              ]}
              onRowClick={(row) => {
                window.location.href = `/terminal/aptos/dex/${row.slug}`;
              }}
            />
          </div>
        )}
      </div>
    </TerminalLayout>
  );
}

