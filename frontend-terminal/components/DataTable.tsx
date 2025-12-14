"use client";

import React from "react";

interface Column {
  key: string;
  label: string;
}

interface DataTableProps {
  data: any[];
  columns: Column[];
  onRowClick?: (row: any) => void;
}

function FeesSourceBadge({ source }: { source: string | null | undefined }) {
  if (!source) return null;
  
  const isReal = source === "aptos_indexer";
  const isHyperionApi = source === "hyperion_api";
  const isEstimate = source === "dexscreener";
  
  let label: string;
  let bgColor: string;
  let tooltip: string;
  
  if (isReal) {
    label = "Onchain";
    bgColor = "bg-green-100 text-green-800";
    tooltip = "Fees calculated from Aptos Indexer fungible asset activities";
  } else if (isHyperionApi) {
    label = "API";
    bgColor = "bg-blue-100 text-blue-800";
    tooltip = "Fees from Hyperion official API";
  } else if (isEstimate) {
    label = "Estimate";
    bgColor = "bg-yellow-100 text-yellow-800";
    tooltip = "Estimated fees from Dexscreener";
  } else {
    label = source;
    bgColor = "bg-gray-100 text-gray-800";
    tooltip = `Fees from ${source}`;
  }
  
  return (
    <span 
      className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${bgColor} cursor-help`}
      title={tooltip}
    >
      {label}
    </span>
  );
}

export default function DataTable({ data, columns, onRowClick }: DataTableProps) {
  const formatValue = (value: any, key: string, row?: any): React.ReactNode => {
    // Special handling for pool column - show token pair
    if (key === "pool" || key === "pair") {
      const token0 = row?.token0_symbol;
      const token1 = row?.token1_symbol;
      
      // If both symbols exist, show as TOKEN0/TOKEN1
      if (token0 && token1) {
        return (
          <div className="flex items-center">
            <span className="font-medium">{token0}/{token1}</span>
          </div>
        );
      }
      // If only one symbol exists, show it with "?"
      if (token0) {
        return <span className="font-medium">{token0}/?</span>;
      }
      if (token1) {
        return <span className="font-medium">?/{token1}</span>;
      }
      // If no symbols, show addresses or "?"
      const addr0 = row?.token0_address;
      const addr1 = row?.token1_address;
      if (addr0 && addr1) {
        return <span className="text-gray-400 text-xs">{addr0.slice(0, 6)}.../{addr1.slice(0, 6)}...</span>;
      }
      return "—";
    }
    
    if (value === null || value === undefined || value === "") {
      return "—";
    }
    if (typeof value === "number") {
      // Форматируем большие числа
      let formatted: string;
      if (value >= 1000000) {
        formatted = `$${(value / 1000000).toFixed(2)}M`;
      } else if (value >= 1000) {
        formatted = `$${(value / 1000).toFixed(2)}K`;
      } else {
        formatted = `$${value.toFixed(2)}`;
      }
      
      // Add fees_source badge for fees columns
      if (key.includes("fees") && row?.fees_source) {
        return (
          <span className="flex items-center">
            {formatted}
            <FeesSourceBadge source={row.fees_source} />
          </span>
        );
      }
      
      return formatted;
    }
    return String(value);
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, idx) => (
            <tr
              key={idx}
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? "cursor-pointer hover:bg-gray-50" : ""}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatValue(row[col.key], col.key, row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

