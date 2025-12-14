"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface ChartCardProps {
  title: string;
  data: any[];
  dataKey: string;
}

export default function ChartCard({ title, data, dataKey }: ChartCardProps) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <p className="text-gray-500 text-center py-8">No data yet</p>
      </div>
    );
  }

  // Format data for recharts
  const chartData = data
    .map((item) => {
      const value = item[dataKey];
      if (value === null || value === undefined) {
        return null;
      }
      return {
        timestamp: item.timestamp ? new Date(item.timestamp).toLocaleDateString() : "",
        value: typeof value === "number" ? value : parseFloat(value) || 0,
      };
    })
    .filter((item) => item !== null);

  if (chartData.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <p className="text-gray-500 text-center py-8">No data yet</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              if (value >= 1000000) {
                return `$${(value / 1000000).toFixed(1)}M`;
              }
              if (value >= 1000) {
                return `$${(value / 1000).toFixed(1)}K`;
              }
              return `$${value.toFixed(0)}`;
            }}
          />
          <Tooltip
            formatter={(value: number) => {
              return `$${value.toLocaleString()}`;
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

