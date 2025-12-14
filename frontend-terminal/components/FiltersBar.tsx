"use client";

interface FiltersBarProps {
  timeframe: string;
  onTimeframeChange: (value: string) => void;
  sort: string;
  onSortChange: (value: string) => void;
  search: string;
  onSearchChange: (value: string) => void;
}

export default function FiltersBar({
  timeframe,
  onTimeframeChange,
  sort,
  onSortChange,
  search,
  onSearchChange,
}: FiltersBarProps) {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Timeframe
          </label>
          <select
            value={timeframe}
            onChange={(e) => onTimeframeChange(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="1d">1 Day</option>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sort
          </label>
          <select
            value={sort}
            onChange={(e) => onSortChange(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="tvl_desc">TVL Desc</option>
            <option value="tvl_asc">TVL Asc</option>
            <option value="volume_desc">Volume Desc</option>
            <option value="name_asc">Name Asc</option>
          </select>
        </div>

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search..."
            className="border rounded px-3 py-2 w-full"
          />
        </div>
      </div>
    </div>
  );
}

